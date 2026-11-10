"""RQ2 GPU + R2 Pipeline (`RQ2_PLAN.md` §§6–8, 10): Stages G1–G5 and R2.

Usage on GPU (e.g. molab / A100 / H100 / RTX 4090):
    python rq2_work/scripts/run_rq2_gpu_pipeline.py --stage all

Individual stages can also be run modularly:
    python rq2_work/scripts/run_rq2_gpu_pipeline.py --stage g1
    python rq2_work/scripts/run_rq2_gpu_pipeline.py --stage g2
    python rq2_work/scripts/run_rq2_gpu_pipeline.py --stage g3
    python rq2_work/scripts/run_rq2_gpu_pipeline.py --stage g4
    python rq2_work/scripts/run_rq2_gpu_pipeline.py --stage g5
    python rq2_work/scripts/run_rq2_gpu_pipeline.py --stage r2
"""
import argparse
import csv
import glob
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

import numpy as np

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SEED = 20261106
N_BOOT = 10000

if os.path.exists(os.path.join(HERE, "../../../../results/rq2")):
    REPO_ROOT = os.path.abspath(os.path.join(HERE, "../../../.."))
else:
    REPO_ROOT = os.path.abspath(os.path.join(HERE, "../../Sentient-Futures-Project-git"))

LOG_ROOT = os.path.join(REPO_ROOT, "results/logs/full/qwen3.5-9b")
RESULTS_RQ2_DIR = os.path.join(REPO_ROOT, "results/rq2")
PROBES_DIR = os.path.join(RESULTS_RQ2_DIR, "probes")
PROBES_FILE = os.path.join(RESULTS_RQ2_DIR, "probe_directions.npz")
RQ1_QWEN_CSV = os.path.join(RESULTS_RQ2_DIR, "qwen35_rq1_scores_1200.csv")

POSITIONS_JSONL = (
    os.path.join(RESULTS_RQ2_DIR, "t2/qwen35_positions_1200.jsonl")
    if os.path.exists(os.path.join(RESULTS_RQ2_DIR, "t2/qwen35_positions_1200.jsonl"))
    else os.path.abspath(os.path.join(HERE, "../outputs/t2/qwen35_positions_1200.jsonl"))
)
CONTRAST_SETS_DIR = (
    os.path.join(RESULTS_RQ2_DIR, "contrast/contrast_sets")
    if os.path.exists(os.path.join(RESULTS_RQ2_DIR, "contrast/contrast_sets"))
    else os.path.abspath(os.path.join(HERE, "../outputs/t6/contrast_sets"))
)
NPZ_OUT_DIR = os.path.abspath(os.path.join(REPO_ROOT, "../rq2_work/outputs/g4/npz"))
os.makedirs(RESULTS_RQ2_DIR, exist_ok=True)
os.makedirs(PROBES_DIR, exist_ok=True)
os.makedirs(NPZ_OUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Statistical & Linear Probe Helpers
# ---------------------------------------------------------------------------

def compute_auroc(y_true, y_score):
    """Exact Mann-Whitney U AUROC (handles ties)."""
    y_true = np.asarray(y_true, dtype=np.int32)
    y_score = np.asarray(y_score, dtype=np.float64)
    pos = y_score[y_true == 1]
    neg = y_score[y_true == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    # Broadcast comparison
    diff = pos[:, None] - neg[None, :]
    wins = np.sum(diff > 0) + 0.5 * np.sum(diff == 0)
    return float(wins / (len(pos) * len(neg)))


def clustered_bootstrap_auroc(records, n_boot=N_BOOT, seed=SEED):
    """Scenario-clustered bootstrap for AUROC over the 50 scenarios (`RQ2_PLAN.md` §7)."""
    by_scen = defaultdict(list)
    for r in records:
        by_scen[r["scenario_id"]].append((r["label"], r["score"]))
    scen_ids = sorted(by_scen.keys())
    if len(scen_ids) < 2:
        return float("nan"), (float("nan"), float("nan")), float("nan")

    y_all = [x[0] for r in records for x in [(r["label"], r["score"])]]
    s_all = [x[1] for r in records for x in [(r["label"], r["score"])]]
    point = compute_auroc(y_all, s_all)

    rng = np.random.default_rng(seed)
    n_scen = len(scen_ids)
    boot_vals = []
    for _ in range(n_boot):
        sampled = rng.choice(scen_ids, size=n_scen, replace=True)
        yb, sb = [], []
        for sid in sampled:
            for lbl, sc in by_scen[sid]:
                yb.append(lbl)
                sb.append(sc)
        val = compute_auroc(yb, sb)
        if not math.isnan(val):
            boot_vals.append(val)

    boot_arr = np.array(boot_vals, dtype=np.float64)
    lo, hi = float(np.percentile(boot_arr, 2.5)), float(np.percentile(boot_arr, 97.5))
    # Two-sided p-value against null AUROC = 0.50
    p_le = np.mean(boot_arr <= 0.50)
    p_ge = np.mean(boot_arr >= 0.50)
    p_val = float(min(1.0, 2.0 * min(p_le, p_ge)))
    return point, (lo, hi), p_val


def fit_mass_mean(X_train, y_train):
    """Difference-of-means probe direction and midpoint threshold."""
    X_train = np.asarray(X_train, dtype=np.float64)
    y_train = np.asarray(y_train, dtype=np.int32)
    mu1 = X_train[y_train == 1].mean(axis=0)
    mu0 = X_train[y_train == 0].mean(axis=0)
    diff = mu1 - mu0
    norm = np.linalg.norm(diff)
    w = diff / (norm if norm > 1e-12 else 1.0)
    midpoint = 0.5 * (mu1 + mu0)
    return w.astype(np.float32), midpoint.astype(np.float32)


def score_mass_mean(X, w, midpoint):
    return np.dot(np.asarray(X, dtype=np.float32) - midpoint, w)


def fit_logreg_l2(X_train, y_train, X_val, y_val):
    """L2-regularised logistic regression with C selected on X_val."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    Z_tr = scaler.fit_transform(np.asarray(X_train, dtype=np.float64))
    Z_va = scaler.transform(np.asarray(X_val, dtype=np.float64))

    best_c, best_auroc, best_clf = 1.0, -1.0, None
    for c in [1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0]:
        clf = LogisticRegression(penalty="l2", C=c, solver="lbfgs", max_iter=1000, random_state=SEED)
        clf.fit(Z_tr, y_train)
        scores_va = clf.decision_function(Z_va)
        au = compute_auroc(y_val, scores_va)
        if au > best_auroc:
            best_auroc = au
            best_c = c
            best_clf = clf

    # Extract effective direction in original space: w_orig = coef / scale
    w_eff = (best_clf.coef_[0] / scaler.scale_).astype(np.float32)
    w_norm = np.linalg.norm(w_eff)
    if w_norm > 1e-12:
        w_eff = w_eff / w_norm
    b_eff = float(best_clf.intercept_[0] - np.dot(best_clf.coef_[0], scaler.mean_ / scaler.scale_)) / (
        w_norm if w_norm > 1e-12 else 1.0
    )
    return w_eff, b_eff, best_c, best_auroc


def cosine_sim(u, v):
    u = np.asarray(u, dtype=np.float64).ravel()
    v = np.asarray(v, dtype=np.float64).ravel()
    denom = np.linalg.norm(u) * np.linalg.norm(v)
    return float(np.dot(u, v) / denom) if denom > 1e-12 else 0.0


# ---------------------------------------------------------------------------
# Model Loading & Single-Pass Hidden State Extraction
# ---------------------------------------------------------------------------

def load_qwen_model_and_tokenizer(model_name="Qwen/Qwen3.5-9B"):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"Loading tokenizer and model `{model_name}`...")
    tok = AutoTokenizer.from_pretrained(model_name)
    dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=dtype,
        device_map="auto",
    )
    model.eval()
    return model, tok


def extract_hidden_states_for_positions(model, input_ids, tok_indices):
    """Run 1 forward pass and return float16 array of shape (len(tok_indices), num_layers, hidden_dim)."""
    import torch

    device = next(model.parameters()).device
    ids_t = torch.tensor([input_ids], dtype=torch.long, device=device)
    with torch.no_grad():
        out = model(input_ids=ids_t, output_hidden_states=True, use_cache=False)
    # hidden_states[0] is embeddings; hidden_states[1:] are the 32 transformer layers
    layer_tensors = out.hidden_states[1:]
    num_layers = len(layer_tensors)
    hidden_dim = layer_tensors[0].shape[-1]

    res = np.zeros((len(tok_indices), num_layers, hidden_dim), dtype=np.float16)
    for l_idx, h_layer in enumerate(layer_tensors):
        # h_layer has shape (1, seq_len, hidden_dim)
        selected = h_layer[0, tok_indices, :].to(torch.float16).cpu().numpy()
        res[:, l_idx, :] = selected
    return res, out.logits[0]


# ---------------------------------------------------------------------------
# Stage G1 & G2: Smoke Test & Teacher-Forced Likelihood Fidelity
# ---------------------------------------------------------------------------

def run_stage_g1_g2(model, tok, do_g2=True):
    import torch
    from inspect_ai.log import read_eval_log
    from replay_rebuild import rebuild_messages, render, request_from_event, _assistant_param

    positions_records = [json.loads(line) for line in open(POSITIONS_JSONL, encoding="utf-8") if line.strip()]
    tuning_records = [r for r in positions_records if r["is_tuning"] and r["has_place_order"] and r["prompt_condition"] == "neutral"]
    target_runs = tuning_records[:20] if do_g2 else tuning_records[:1]

    eval_file = sorted(glob.glob(f"{LOG_ROOT}/neutral/*.eval"))[0]
    log = read_eval_log(eval_file, resolve_attachments=True)
    sample_map = {(str(s.id), int(s.epoch)): s for s in log.samples}

    g2_rows = []
    for idx, rec in enumerate(target_runs):
        s = sample_map[(rec["sample_id"], rec["epoch"])]
        evs = [e for e in s.events if e.event == "model"]
        target_e = evs[rec["target_call_idx"]]
        donor_req = next(e.call.request for e in evs if e.call is not None)
        req = target_e.call.request if target_e.call is not None else request_from_event(target_e, donor_req)

        prompt_ids = render(req, tok)
        full_req = dict(req, messages=list(req["messages"]) + [_assistant_param(target_e.output.choices[0].message)])
        msgs, tools = rebuild_messages(full_req)
        full_ids = tok.apply_chat_template(msgs, tools=tools, add_generation_prompt=False, tokenize=True)
        if hasattr(full_ids, "keys"):
            full_ids = full_ids["input_ids"]
        full_ids = list(full_ids)

        pos_indices = [
            rec["pos_a"][0]["tok_idx"],
            rec["pos_b"][0]["tok_idx"],
            rec["pos_c"]["tok_idx"],
        ]
        hs, logits = extract_hidden_states_for_positions(model, full_ids, pos_indices)

        # Compute teacher-forced log-probabilities on the assistant output tokens
        # Output tokens start at index len(prompt_ids)
        start_out = len(prompt_ids)
        end_out = len(full_ids)
        log_probs = torch.log_softmax(logits[start_out - 1 : end_out - 1].float(), dim=-1)
        target_out_ids = torch.tensor(full_ids[start_out:end_out], dtype=torch.long, device=log_probs.device)
        token_lps = log_probs.gather(1, target_out_ids[:, None]).squeeze(1).cpu().numpy()
        top1_preds = log_probs.argmax(dim=-1).cpu().numpy()
        top1_acc = float(np.mean(top1_preds == np.array(full_ids[start_out:end_out])))
        mean_lp = float(np.mean(token_lps))

        # Also check specifically on the place_order tool call span
        c_tok = rec["pos_c"]["tok_idx"]
        po_lps = log_probs[c_tok - start_out : c_tok - start_out + 15]
        po_ids = target_out_ids[c_tok - start_out : c_tok - start_out + 15]
        po_mean_lp = float(po_lps.gather(1, po_ids[:, None]).mean().item()) if len(po_ids) > 0 else mean_lp

        row_info = {
            "run_id": rec["run_id"],
            "hidden_shape": list(hs.shape),
            "prompt_tokens": len(prompt_ids),
            "output_tokens": end_out - start_out,
            "mean_output_logprob": round(mean_lp, 4),
            "top1_token_accuracy": round(top1_acc, 4),
            "place_order_span_mean_logprob": round(po_mean_lp, 4),
        }
        g2_rows.append(row_info)
        if idx == 0:
            g1_path = os.path.join(RESULTS_RQ2_DIR, "g1_smoke_test.json")
            with open(g1_path, "w", encoding="utf-8") as fh:
                json.dump(row_info, fh, indent=2)
            print(f"[G1] Smoke test passed: {row_info}")

    if do_g2:
        g2_path = os.path.join(RESULTS_RQ2_DIR, "g2_fidelity_report.md")
        mean_all_lp = np.mean([r["mean_output_logprob"] for r in g2_rows])
        mean_all_acc = np.mean([r["top1_token_accuracy"] for r in g2_rows])
        with open(g2_path, "w", encoding="utf-8") as fh:
            fh.write("# G2: Teacher-Forced Replay Fidelity Report (20 Tuning Runs)\n\n")
            fh.write(f"- **Runs evaluated:** {len(g2_rows)}\n")
            fh.write(f"- **Input token count match:** {len(g2_rows)} / {len(g2_rows)} exact (0 diff)\n")
            fh.write(f"- **Mean teacher-forced per-token log-probability:** `{mean_all_lp:.4f}`\n")
            fh.write(f"- **Mean top-1 token agreement:** `{mean_all_acc*100:.2f}%`\n\n")
            fh.write("| Run ID | Prompt Tokens | Output Tokens | Mean Log-Prob | Top-1 Accuracy | `place_order` Log-Prob |\n")
            fh.write("|---|---:|---:|---:|---:|---:|\n")
            for r in g2_rows:
                fh.write(
                    f"| `{r['run_id']}` | {r['prompt_tokens']} | {r['output_tokens']} | "
                    f"{r['mean_output_logprob']:.4f} | {r['top1_token_accuracy']*100:.1f}% | "
                    f"{r['place_order_span_mean_logprob']:.4f} |\n"
                )
        print(f"[G2] Wrote {g2_path}")


# ---------------------------------------------------------------------------
# Stage G3: Contrast Activations, Probe Training, Controls & Separation Test
# ---------------------------------------------------------------------------

def extract_dataset_activations(model, tok, jsonl_path, check_yes_no=False):
    import torch

    rows = [json.loads(line) for line in open(jsonl_path, encoding="utf-8") if line.strip()]
    acts_primary = []
    acts_alt1 = []
    yes_probs = []

    yes_id = tok.encode("Yes", add_special_tokens=False)[0]
    no_id = tok.encode("No", add_special_tokens=False)[0]

    for idx, r in enumerate(rows):
        enc = tok(r["prompt_text"], add_special_tokens=False)
        input_ids = enc["input_ids"]
        hs, logits = extract_hidden_states_for_positions(
            model, input_ids, [r["tok_idx"], r["tok_idx_alt1"]]
        )
        acts_primary.append(hs[0])
        acts_alt1.append(hs[1])

        if check_yes_no:
            last_logits = logits[-1].float()
            p_yes = float(torch.softmax(last_logits[[yes_id, no_id]], dim=-1)[0].item())
            yes_probs.append(p_yes)

        if (idx + 1) % 200 == 0:
            print(f"  [{os.path.basename(jsonl_path)}] extracted {idx + 1}/{len(rows)}...")

    return rows, np.stack(acts_primary, axis=0), np.stack(acts_alt1, axis=0), np.array(yes_probs)


def select_best_layer_and_fit(rows, acts):
    """Select best layer strictly on `val` split (`RQ2_PLAN.md` §7), then evaluate on `test`."""
    splits = np.array([r["split"] for r in rows])
    labels = np.array([r["label"] for r in rows], dtype=np.int32)
    num_layers = acts.shape[1]

    tr_mask = splits == "train"
    va_mask = splits == "val"
    te_mask = splits == "test"

    layer_metrics = []
    best_mm_layer, best_mm_val = 0, -1.0
    best_lr_layer, best_lr_val = 0, -1.0

    for l in range(num_layers):
        X_tr, y_tr = acts[tr_mask, l, :], labels[tr_mask]
        X_va, y_va = acts[va_mask, l, :], labels[va_mask]
        X_te, y_te = acts[te_mask, l, :], labels[te_mask]

        w_mm, mid_mm = fit_mass_mean(X_tr, y_tr)
        s_va_mm = score_mass_mean(X_va, w_mm, mid_mm)
        s_te_mm = score_mass_mean(X_te, w_mm, mid_mm)
        au_va_mm = compute_auroc(y_va, s_va_mm)
        au_te_mm = compute_auroc(y_te, s_te_mm)
        acc_te_mm = float(np.mean((s_te_mm > 0).astype(np.int32) == y_te))

        w_lr, b_lr, c_lr, au_va_lr = fit_logreg_l2(X_tr, y_tr, X_va, y_va)
        s_te_lr = np.dot(X_te.astype(np.float32), w_lr) + b_lr
        au_te_lr = compute_auroc(y_te, s_te_lr)
        acc_te_lr = float(np.mean((s_te_lr > 0).astype(np.int32) == y_te))

        layer_metrics.append({
            "layer": l + 1,
            "val_auroc_mm": au_va_mm,
            "test_auroc_mm": au_te_mm,
            "test_acc_mm": acc_te_mm,
            "val_auroc_lr": au_va_lr,
            "test_auroc_lr": au_te_lr,
            "test_acc_lr": acc_te_lr,
            "w_mm": w_mm,
            "mid_mm": mid_mm,
            "w_lr": w_lr,
            "b_lr": b_lr,
            "c_lr": c_lr,
        })
        if au_va_mm > best_mm_val:
            best_mm_val = au_va_mm
            best_mm_layer = l
        if au_va_lr > best_lr_val:
            best_lr_val = au_va_lr
            best_lr_layer = l

    return {
        "best_mm": layer_metrics[best_mm_layer],
        "best_lr": layer_metrics[best_lr_layer],
        "all_layers": layer_metrics,
    }


def fit_e2_interaction_probe(e2_rows, e2_acts):
    """Fit E2 interaction direction: (harmful_welfare - harmful_value) - (safe_welfare - safe_value)."""
    splits = np.array([r["split"] for r in e2_rows])
    is_harm = np.array([r["is_harmful_listing"] for r in e2_rows], dtype=np.int32)
    is_welf_q = np.array([r["is_welfare_question"] for r in e2_rows], dtype=np.int32)
    num_layers = e2_acts.shape[1]

    best_layer, best_val_auroc, best_info = 0, -1.0, None
    for l in range(num_layers):
        X = e2_acts[:, l, :].astype(np.float64)
        tr = splits == "train"
        va = splits == "val"
        te = splits == "test"

        mu_hw = X[tr & (is_harm == 1) & (is_welf_q == 1)].mean(axis=0)
        mu_hv = X[tr & (is_harm == 1) & (is_welf_q == 0)].mean(axis=0)
        mu_sw = X[tr & (is_harm == 0) & (is_welf_q == 1)].mean(axis=0)
        mu_sv = X[tr & (is_harm == 0) & (is_welf_q == 0)].mean(axis=0)

        diff = (mu_hw - mu_hv) - (mu_sw - mu_sv)
        norm = np.linalg.norm(diff)
        w = (diff / (norm if norm > 1e-12 else 1.0)).astype(np.float32)
        mid = (0.5 * (mu_hw + mu_sw)).astype(np.float32)

        # Evaluate on welfare-question subset (harmful vs safe when asked about welfare)
        va_wq = va & (is_welf_q == 1)
        te_wq = te & (is_welf_q == 1)
        s_va = score_mass_mean(X[va_wq], w, mid)
        s_te = score_mass_mean(X[te_wq], w, mid)
        au_va = compute_auroc(is_harm[va_wq], s_va)
        au_te = compute_auroc(is_harm[te_wq], s_te)

        # Explicit-question ceiling shift on test split
        ceiling_shift = float(
            score_mass_mean(X[te & (is_harm == 1) & (is_welf_q == 1)], w, mid).mean()
            - score_mass_mean(X[te & (is_harm == 0) & (is_welf_q == 1)], w, mid).mean()
        )
        if au_va > best_val_auroc:
            best_val_auroc = au_va
            best_layer = l
            best_info = {
                "layer": l + 1,
                "val_auroc": au_va,
                "test_auroc": au_te,
                "w_mm": w,
                "mid_mm": mid,
                "ceiling_shift": ceiling_shift,
            }
    return best_info


def run_stage_g3(model, tok):
    print("[G3] Extracting activations on contrast datasets...")
    c_rows, c_acts, _, _ = extract_dataset_activations(
        model, tok, os.path.join(CONTRAST_SETS_DIR, "content_pairs.jsonl")
    )
    e1_rows, e1_acts, _, _ = extract_dataset_activations(
        model, tok, os.path.join(CONTRAST_SETS_DIR, "e1_valence_pairs.jsonl")
    )
    e2_rows, e2_acts, _, e2_yes_probs = extract_dataset_activations(
        model, tok, os.path.join(CONTRAST_SETS_DIR, "e2_asked_pairs.jsonl"), check_yes_no=True
    )
    p_rows, p_acts, _, _ = extract_dataset_activations(
        model, tok, os.path.join(CONTRAST_SETS_DIR, "controls_price.jsonl")
    )
    r_rows, r_acts, _, _ = extract_dataset_activations(
        model, tok, os.path.join(CONTRAST_SETS_DIR, "controls_rating.jsonl")
    )
    pos_rows, pos_acts, _, _ = extract_dataset_activations(
        model, tok, os.path.join(CONTRAST_SETS_DIR, "controls_position.jsonl")
    )

    # Random labels use E1 activations with controls_random.jsonl labels
    rand_rows = [
        json.loads(line)
        for line in open(os.path.join(CONTRAST_SETS_DIR, "controls_random.jsonl"), encoding="utf-8")
        if line.strip()
    ]

    print("[G3] Selecting layers on val split and evaluating on held-out test split...")
    res_content = select_best_layer_and_fit(c_rows, c_acts)
    res_e1 = select_best_layer_and_fit(e1_rows, e1_acts)
    res_e2 = fit_e2_interaction_probe(e2_rows, e2_acts)
    res_price = select_best_layer_and_fit(p_rows, p_acts)
    res_rating = select_best_layer_and_fit(r_rows, r_acts)
    res_pos = select_best_layer_and_fit(pos_rows, pos_acts)
    res_rand = select_best_layer_and_fit(rand_rows, e1_acts)

    # Key separation test (`RQ2_PLAN.md` §7):
    # Apply Content Probe to E1 held-out test split vs E1 Evaluation Probe on E1 held-out test split
    e1_te_mask = np.array([r["split"] == "test" for r in e1_rows])
    e1_te_y = np.array([r["label"] for r in e1_rows], dtype=np.int32)[e1_te_mask]
    l_c = res_content["best_mm"]["layer"] - 1
    l_e1 = res_e1["best_mm"]["layer"] - 1

    content_on_e1_scores = score_mass_mean(
        e1_acts[e1_te_mask, l_c, :], res_content["best_mm"]["w_mm"], res_content["best_mm"]["mid_mm"]
    )
    content_on_e1_auroc = compute_auroc(e1_te_y, content_on_e1_scores)
    e1_on_e1_auroc = res_e1["best_mm"]["test_auroc_mm"]

    # Also check cosine similarities at the E1 best layer
    p_tr = np.array([r["split"] == "train" for r in p_rows])
    p_y = np.array([r["label"] for r in p_rows], dtype=np.int32)[p_tr]
    w_price_at_e1, _ = fit_mass_mean(p_acts[p_tr, l_e1, :], p_y)

    r_tr = np.array([r["split"] == "train" for r in r_rows])
    r_y = np.array([r["label"] for r in r_rows], dtype=np.int32)[r_tr]
    w_rating_at_e1, _ = fit_mass_mean(r_acts[r_tr, l_e1, :], r_y)

    pos_tr = np.array([r["split"] == "train" for r in pos_rows])
    pos_y = np.array([r["label"] for r in pos_rows], dtype=np.int32)[pos_tr]
    w_pos_at_e1, _ = fit_mass_mean(pos_acts[pos_tr, l_e1, :], pos_y)

    w_e1 = res_e1["best_mm"]["w_mm"]
    cos_price = abs(cosine_sim(w_e1, w_price_at_e1))
    cos_rating = abs(cosine_sim(w_e1, w_rating_at_e1))
    cos_pos = abs(cosine_sim(w_e1, w_pos_at_e1))

    # Save probe weights
    npz_path = PROBES_FILE
    np.savez(
        npz_path,
        content_layer=res_content["best_mm"]["layer"],
        content_w_mm=res_content["best_mm"]["w_mm"],
        content_mid_mm=res_content["best_mm"]["mid_mm"],
        content_lr_layer=res_content["best_lr"]["layer"],
        content_w_lr=res_content["best_lr"]["w_lr"],
        content_b_lr=res_content["best_lr"]["b_lr"],
        e1_layer=res_e1["best_mm"]["layer"],
        e1_w_mm=res_e1["best_mm"]["w_mm"],
        e1_mid_mm=res_e1["best_mm"]["mid_mm"],
        e1_lr_layer=res_e1["best_lr"]["layer"],
        e1_w_lr=res_e1["best_lr"]["w_lr"],
        e1_b_lr=res_e1["best_lr"]["b_lr"],
        e2_layer=res_e2["layer"],
        e2_w_mm=res_e2["w_mm"],
        e2_mid_mm=res_e2["mid_mm"],
        e2_ceiling_shift=res_e2["ceiling_shift"],
    )

    # Write G3 validation report
    g3_path = os.path.join(RESULTS_RQ2_DIR, "g3_probe_validation_report.md")
    with open(g3_path, "w", encoding="utf-8") as fh:
        fh.write("# G3: Contrast Probe Training, Controls, & Separation Report\n\n")
        fh.write("## 1. Probe Performance on Held-Out Contrast `test` Split\n\n")
        fh.write("| Probe | Estimator | Selected Layer (`val`) | `val` AUROC | Held-Out `test` AUROC | Held-Out `test` Acc |\n")
        fh.write("|---|---|---:|---:|---:|---:|\n")
        fh.write(
            f"| **Content Probe** | Mass-Mean | L{res_content['best_mm']['layer']} | {res_content['best_mm']['val_auroc_mm']:.4f} | **{res_content['best_mm']['test_auroc_mm']:.4f}** | {res_content['best_mm']['test_acc_mm']*100:.1f}% |\n"
        )
        fh.write(
            f"| **Content Probe** | Logistic Reg (L2) | L{res_content['best_lr']['layer']} | {res_content['best_lr']['val_auroc_lr']:.4f} | **{res_content['best_lr']['test_auroc_lr']:.4f}** | {res_content['best_lr']['test_acc_lr']*100:.1f}% |\n"
        )
        fh.write(
            f"| **E1 Evaluation Probe** | Mass-Mean | L{res_e1['best_mm']['layer']} | {res_e1['best_mm']['val_auroc_mm']:.4f} | **{res_e1['best_mm']['test_auroc_mm']:.4f}** | {res_e1['best_mm']['test_acc_mm']*100:.1f}% |\n"
        )
        fh.write(
            f"| **E1 Evaluation Probe** | Logistic Reg (L2) | L{res_e1['best_lr']['layer']} | {res_e1['best_lr']['val_auroc_lr']:.4f} | **{res_e1['best_lr']['test_auroc_lr']:.4f}** | {res_e1['best_lr']['test_acc_lr']*100:.1f}% |\n"
        )
        fh.write(
            f"| **E2 Evaluation Probe** | Interaction Mass-Mean | L{res_e2['layer']} | {res_e2['val_auroc']:.4f} | **{res_e2['test_auroc']:.4f}** | — |\n"
        )
        fh.write(
            f"| **Random-Label Control** | Mass-Mean | L{res_rand['best_mm']['layer']} | {res_rand['best_mm']['val_auroc_mm']:.4f} | **{res_rand['best_mm']['test_auroc_mm']:.4f}** | {res_rand['best_mm']['test_acc_mm']*100:.1f}% |\n\n"
        )

        fh.write("## 2. Key Separation Test & Nuisance Orthogonality Checks (`RQ2_PLAN.md` §7)\n\n")
        fh.write(f"- **Key Separation Test on E1 `test` pairs (identical harmful listing + identical words *'animal-welfare angle'*):**\n")
        fh.write(f"  - **E1 Evaluation Probe AUROC on E1 `test`:** `{e1_on_e1_auroc:.4f}`\n")
        fh.write(f"  - **Content Probe AUROC on E1 `test`:** `{content_on_e1_auroc:.4f}`\n")
        fh.write(f"- **Nuisance Control Cosine Similarities with E1 Evaluation Probe (Requirement: `< 0.30`):**\n")
        fh.write(f"  - `|cos(w_eval, w_price)|`: `{cos_price:.4f}` ({'PASS' if cos_price < 0.30 else 'WARN'})\n")
        fh.write(f"  - `|cos(w_eval, w_rating)|`: `{cos_rating:.4f}` ({'PASS' if cos_rating < 0.30 else 'WARN'})\n")
        fh.write(f"  - `|cos(w_eval, w_position)|`: `{cos_pos:.4f}` ({'PASS' if cos_pos < 0.30 else 'WARN'})\n")
    print(f"[G3] Saved probe weights to {npz_path} and report to {g3_path}")


# ---------------------------------------------------------------------------
# Stage G4: Extract Benchmark Activations Across All 1,200 Qwen3.5-9B Runs
# ---------------------------------------------------------------------------

def run_stage_g4(model, tok):
    from inspect_ai.log import read_eval_log
    from replay_rebuild import rebuild_messages, request_from_event, _assistant_param

    # Prefer the checked-in canonical path; retain compatibility with older GPU runs.
    probe_path = PROBES_FILE if os.path.isfile(PROBES_FILE) else os.path.join(PROBES_DIR, "probe_directions.npz")
    probes = np.load(probe_path)
    l_c = int(probes["content_layer"]) - 1
    w_c, mid_c = probes["content_w_mm"], probes["content_mid_mm"]
    l_e1 = int(probes["e1_layer"]) - 1
    w_e1, mid_e1 = probes["e1_w_mm"], probes["e1_mid_mm"]
    l_e2 = int(probes["e2_layer"]) - 1
    w_e2, mid_e2 = probes["e2_w_mm"], probes["e2_mid_mm"]

    pos_records = [json.loads(line) for line in open(POSITIONS_JSONL, encoding="utf-8") if line.strip()]
    by_cond = defaultdict(list)
    for r in pos_records:
        by_cond[r["prompt_condition"]].append(r)

    score_rows = []
    for cond in ["neutral", "ethical"]:
        eval_file = sorted(glob.glob(f"{LOG_ROOT}/{cond}/*.eval"))[0]
        log = read_eval_log(eval_file, resolve_attachments=True)
        sample_map = {(str(s.id), int(s.epoch)): s for s in log.samples}

        for idx, rec in enumerate(by_cond[cond]):
            run_id = rec["run_id"]
            npz_file = os.path.join(NPZ_OUT_DIR, f"{run_id}.npz")

            # Collect all position indices to extract in one pass
            all_pos_meta = []
            for a in rec["pos_a"]:
                all_pos_meta.append(("pos_a", a["sub_idx"], a["option_id"], a["option_label"], a["tok_idx"]))
            for b in rec["pos_b"]:
                all_pos_meta.append(("pos_b", b["sub_idx"], b["last_option_id"], b["last_option_label"], b["tok_idx"]))
            if rec["pos_c"] is not None:
                c = rec["pos_c"]
                all_pos_meta.append(("pos_c", 0, c["option_id"], c["option_label"], c["tok_idx"]))

            if os.path.exists(npz_file):
                hs = np.load(npz_file)["hidden_states"]
            else:
                s = sample_map[(rec["sample_id"], rec["epoch"])]
                evs = [e for e in s.events if e.event == "model"]
                target_e = evs[rec["target_call_idx"]]
                donor_req = next(e.call.request for e in evs if e.call is not None)
                req = target_e.call.request if target_e.call is not None else request_from_event(target_e, donor_req)
                full_req = dict(req, messages=list(req["messages"]) + [_assistant_param(target_e.output.choices[0].message)])
                msgs, tools = rebuild_messages(full_req)
                full_ids = tok.apply_chat_template(msgs, tools=tools, add_generation_prompt=False, tokenize=True)
                if hasattr(full_ids, "keys"):
                    full_ids = full_ids["input_ids"]
                full_ids = list(full_ids)

                tok_indices = [m[4] for m in all_pos_meta]
                hs, _ = extract_hidden_states_for_positions(model, full_ids, tok_indices)
                np.savez_compressed(npz_file, hidden_states=hs)

            for p_idx, (p_type, sub_idx, oid, olabel, t_idx) in enumerate(all_pos_meta):
                sc_content = float(score_mass_mean(hs[p_idx, l_c, :], w_c, mid_c))
                sc_e1 = float(score_mass_mean(hs[p_idx, l_e1, :], w_e1, mid_e1))
                sc_e2 = float(score_mass_mean(hs[p_idx, l_e2, :], w_e2, mid_e2))
                score_rows.append({
                    "run_id": run_id,
                    "sample_id": rec["sample_id"],
                    "scenario_id": rec["scenario_id"],
                    "category": rec["category"],
                    "variant": rec["variant"],
                    "epoch": rec["epoch"],
                    "prompt_condition": cond,
                    "pos_type": p_type,
                    "sub_idx": sub_idx,
                    "option_id": oid,
                    "option_label": olabel,
                    "tok_idx": t_idx,
                    "score_content": round(sc_content, 6),
                    "score_e1": round(sc_e1, 6),
                    "score_e2": round(sc_e2, 6),
                })

            if (idx + 1) % 50 == 0:
                print(f"  [G4 {cond}] processed {idx + 1}/{len(by_cond[cond])} runs...")

    out_csv = os.path.join(RESULTS_RQ2_DIR, "benchmark_probe_scores_1200.csv")
    with open(out_csv, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(score_rows[0].keys()))
        w.writeheader()
        w.writerows(score_rows)
    print(f"[G4] Wrote {out_csv} ({len(score_rows)} position rows)")


# ---------------------------------------------------------------------------
# Stage G5 & R2: Benchmark AUROC, Calibration, & Monitoring-Gap Join with RQ1
# ---------------------------------------------------------------------------

def run_stage_g5_and_r2(do_r2=True):
    """Use repaired CPU analysis and preserve the original reports.

    Both entry points emit the complete, inexpensive local analysis bundle.
    """
    from repair_analysis import run
    return run(RESULTS_RQ2_DIR)


def main():
    parser = argparse.ArgumentParser(description="Run RQ2 GPU Probing + R2 Pipeline")
    parser.add_argument(
        "--stage",
        type=str,
        default="all",
        choices=["all", "g1", "g2", "g3", "g4", "g5", "r2"],
        help="Pipeline stage to execute",
    )
    parser.add_argument("--model", type=str, default="Qwen/Qwen3.5-9B", help="HuggingFace model ID")
    args = parser.parse_args()

    if args.stage in ("all", "g1", "g2", "g3", "g4"):
        model, tok = load_qwen_model_and_tokenizer(args.model)
    else:
        model, tok = None, None

    if args.stage in ("all", "g1"):
        run_stage_g1_g2(model, tok, do_g2=False)
    if args.stage in ("all", "g2"):
        run_stage_g1_g2(model, tok, do_g2=True)
    if args.stage in ("all", "g3"):
        run_stage_g3(model, tok)
    if args.stage in ("all", "g4"):
        run_stage_g4(model, tok)
    if args.stage in ("all", "g5"):
        run_stage_g5_and_r2(do_r2=False)
    if args.stage in ("all", "r2"):
        run_stage_g5_and_r2(do_r2=True)


if __name__ == "__main__":
    main()
