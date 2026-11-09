"""T2: Position Finder across all 1,200 Qwen3.5-9B runs (RQ2_PLAN.md §§6.1, 6.3, 10).

Locates exact 0-based token indices in the single teacher-forced replay sequence for:
  (a) Per-option (pos_a): end of each `get_option_details` tool response
  (b) Persistence (pos_b): start of the assistant's next turn after reading `get_option_details`
  (c) Action time (pos_c): token immediately before `option_id` inside `place_order`

Also verifies exact input token count match (`len(prompt_ids) == usage.input_tokens`)
across all 1,200 Qwen3.5-9B runs, writes the index files, and produces
`outputs/t2/T2_POSITION_REPORT.md` with 5 hand-checked tuning-scenario runs highlighted.
"""
import csv
import glob
import json
import os
import re
import sys
from collections import Counter

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from inspect_ai.log import read_eval_log
from transformers import AutoTokenizer
from replay_rebuild import rebuild_messages, render, request_from_event, _assistant_param

if os.path.exists(os.path.join(HERE, "../../../../results/rq2")):
    REPO_ROOT = os.path.abspath(os.path.join(HERE, "../../../.."))
    TUNING_PATH = os.path.join(REPO_ROOT, "results/rq2/tuning_scenarios.json")
    OUT_DIR = os.path.join(REPO_ROOT, "results/rq2/t2")
else:
    REPO_ROOT = os.path.abspath(os.path.join(HERE, "../../Sentient-Futures-Project-git"))
    TUNING_PATH = os.path.join(HERE, "../outputs/tuning_scenarios.json")
    OUT_DIR = os.path.abspath(os.path.join(HERE, "../outputs/t2"))

LOG_ROOT = os.path.join(REPO_ROOT, "results/logs/full/qwen3.5-9b")
DATASET_PATH = os.path.join(REPO_ROOT, "domains/menu_planning/data/processed/dataset.json")
os.makedirs(OUT_DIR, exist_ok=True)

VARIANTS = ["base", "price_swap", "rating_swap", "reversed"]


def parse_sample_id(sample_id: str):
    for v in VARIANTS:
        suffix = f"_{v}"
        if sample_id.endswith(suffix):
            return sample_id[: -len(suffix)], v
    return sample_id, "unknown"


def load_option_lookup():
    data = json.load(open(DATASET_PATH, encoding="utf-8"))
    lookup = {}
    scenario_meta = {}
    for sc in data["scenarios"]:
        sid = sc["id"]
        h_set = set(sc.get("harmful_ids", []))
        s_set = set(sc.get("safe_ids", []))
        scenario_meta[sid] = {
            "category": sc.get("category", ""),
            "harmful_ids": sorted(h_set),
            "safe_ids": sorted(s_set),
        }
        for exp in sc.get("experiences", []):
            oid = exp["id"]
            if oid in h_set:
                lbl = "harmful"
            elif oid in s_set:
                lbl = "safe"
            else:
                lbl = "distractor"
            lookup[(sid, oid)] = lbl
    return lookup, scenario_meta


def char_to_tok_idx(offsets, char_pos):
    # Binary search for token span [st, en) containing char_pos
    lo, hi = 0, len(offsets) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        st, en = offsets[mid]
        if st <= char_pos < en:
            return mid
        elif char_pos < st:
            hi = mid - 1
        else:
            lo = mid + 1
    return None


def format_highlighted_window(tok, ids, target_idx, label_tag, radius=8):
    pieces = []
    for j in range(max(0, target_idx - radius), min(len(ids), target_idx + radius + 1)):
        t_str = tok.decode([ids[j]]).replace("\n", "\\n")
        if j == target_idx:
            pieces.append(f"**[{label_tag} tok={j}: `{t_str}`]**")
        else:
            pieces.append(f"`{t_str}`")
    return " ".join(pieces)


def main():
    print("Loading dataset.json and tuning scenario IDs...")
    opt_lookup, scenario_meta = load_option_lookup()
    tuning_ids = {d["scenario_id"] for d in json.load(open(TUNING_PATH, encoding="utf-8"))}

    print("Loading Qwen/Qwen3.5-9B tokenizer (local_files_only=True)...")
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3.5-9B", local_files_only=True)

    records = []
    index_rows = []
    hand_check_examples = []

    stats = Counter()
    option_label_counts_a = Counter()
    option_label_counts_b = Counter()
    option_label_counts_c = Counter()

    for cond in ["neutral", "ethical"]:
        eval_files = sorted(glob.glob(f"{LOG_ROOT}/{cond}/*.eval"))
        assert len(eval_files) == 1, f"Expected 1 eval file for {cond}, found {eval_files}"
        print(f"Reading {cond} eval log: {eval_files[0]} ...")
        log = read_eval_log(eval_files[0], resolve_attachments=True)
        print(f"  Loaded {len(log.samples)} samples for {cond}.")

        for s in log.samples:
            sample_id = str(s.id)
            scenario_id, variant = parse_sample_id(sample_id)
            epoch = int(s.epoch)
            is_tuning = scenario_id in tuning_ids
            run_id = f"{cond}__{sample_id}__ep{epoch}"

            evs = [e for e in s.events if e.event == "model"]
            stats["total_runs"] += 1
            stats["total_model_events"] += len(evs)

            # Find donor request for any event missing .call
            def get_donor(idx):
                for j in list(range(idx - 1, -1, -1)) + list(range(idx + 1, len(evs))):
                    if j != idx and evs[j].call is not None:
                        return evs[j].call.request
                return None

            # Find the call that produced the final place_order (or last call if no order)
            target_call_idx = None
            for i, e in enumerate(evs):
                tcs = e.output.choices[0].message.tool_calls or []
                if any(tc.function == "place_order" for tc in tcs):
                    target_call_idx = i

            has_place_order = target_call_idx is not None
            if not has_place_order:
                target_call_idx = len(evs) - 1
                stats["runs_without_place_order"] += 1
            else:
                stats["runs_with_place_order"] += 1

            target_e = evs[target_call_idx]
            donor_req = get_donor(target_call_idx)
            req = (
                target_e.call.request
                if target_e.call is not None
                else request_from_event(target_e, donor_req)
            )

            # Verify input token count on the target call
            prompt_ids = render(req, tok)
            logged_input_tokens = target_e.output.usage.input_tokens
            token_diff = len(prompt_ids) - logged_input_tokens
            if token_diff == 0:
                stats["target_call_exact_match"] += 1
            else:
                stats["target_call_mismatch"] += 1

            # Build teacher-forced full request (prompt + logged assistant response)
            msgs_only = list(req["messages"])
            asst_msg = _assistant_param(target_e.output.choices[0].message)
            full_req = dict(req, messages=msgs_only + [asst_msg])
            msgs, tools = rebuild_messages(full_req)

            full_text = tok.apply_chat_template(
                msgs, tools=tools, add_generation_prompt=False, tokenize=False
            )
            enc = tok(full_text, add_special_tokens=False, return_offsets_mapping=True)
            full_ids = list(enc["input_ids"])
            offsets = enc["offset_mapping"]

            # Optional sanity check on first 20 runs: direct tokenize == offset_mapping tokenize
            if stats["total_runs"] <= 20:
                direct_ids = tok.apply_chat_template(
                    msgs, tools=tools, add_generation_prompt=False, tokenize=True
                )
                if hasattr(direct_ids, "keys"):
                    direct_ids = direct_ids["input_ids"]
                assert list(direct_ids) == full_ids, f"Direct vs offset mismatch on {run_id}"

            # --- LOCATE POSITION (a): Per-option (`get_option_details` results) ---
            # Pattern in full_text:
            # <tool_response>\nOption Details:\n  Name: ...\n  ID: <option_id>\n...</tool_response>
            pos_a_list = []
            tool_resp_pattern = re.compile(
                r"<tool_response>\n(Option Details:\n\s+Name: .*?\n\s+ID: ([^\n]+)\n.*?)\n(</tool_response>)",
                re.DOTALL,
            )
            for m_idx, m in enumerate(tool_resp_pattern.finditer(full_text)):
                oid = m.group(2).strip()
                olabel = opt_lookup.get((scenario_id, oid), "unknown")
                # Last content char of the option details text (just before \n</tool_response>)
                char_content_end = m.end(1) - 1
                char_newline = m.end(1)
                char_close_tag = m.start(3)

                tok_close = char_to_tok_idx(offsets, char_close_tag)
                tok_content_last = char_to_tok_idx(offsets, char_content_end)
                tok_newline = char_to_tok_idx(offsets, char_newline)

                pos_a_item = {
                    "sub_idx": m_idx,
                    "option_id": oid,
                    "option_label": olabel,
                    "tok_idx": tok_close,              # Primary: </tool_response> token
                    "tok_idx_content_last": tok_content_last,  # Alt 1: last content token of listing
                    "tok_idx_newline": tok_newline,    # Alt 2: \n before </tool_response>
                    "char_close_tag": char_close_tag,
                }
                pos_a_list.append(pos_a_item)
                option_label_counts_a[olabel] += 1
                stats["total_pos_a"] += 1

                index_rows.append([
                    run_id, sample_id, scenario_id, variant, epoch, cond, int(is_tuning),
                    "pos_a", m_idx, oid, olabel,
                    tok_close, tok_content_last, tok_newline, len(full_ids)
                ])

            # --- LOCATE POSITION (b): Persistence (first token of assistant's next turn after reading) ---
            # Group get_option_details blocks by the user turn `<|im_start|>user ... <|im_end|>\n<|im_start|>assistant`
            pos_b_list = []
            user_turn_pattern = re.compile(
                r"<\|im_start\|>user\n(.*?)<\|im_end\|>\n(<\|im_start\|>assistant\n<think>\n)",
                re.DOTALL,
            )
            b_idx = 0
            for um in user_turn_pattern.finditer(full_text):
                user_body = um.group(1)
                if "Option Details:\n" not in user_body:
                    continue
                # Find all option_ids read in this user turn
                oids_in_turn = [
                    om.group(2).strip()
                    for om in tool_resp_pattern.finditer(user_body)
                ]
                if not oids_in_turn:
                    continue
                labels_in_turn = [opt_lookup.get((scenario_id, oid), "unknown") for oid in oids_in_turn]
                target_labels = [l for l in labels_in_turn if l in ("harmful", "safe")]
                if len(target_labels) == 0:
                    turn_label = "distractor"
                elif all(l == "harmful" for l in target_labels):
                    turn_label = "harmful"
                elif all(l == "safe" for l in target_labels):
                    turn_label = "safe"
                else:
                    turn_label = "mixed"

                last_oid = oids_in_turn[-1]
                last_olabel = labels_in_turn[-1]

                char_im_start = um.start(2)
                char_think_nl = um.end(2) - 1  # the \n right after <think>
                char_first_gen = um.end(2)     # first generated character after <think>\n

                tok_think_nl = char_to_tok_idx(offsets, char_think_nl)
                tok_im_start = char_to_tok_idx(offsets, char_im_start)
                tok_first_gen = char_to_tok_idx(offsets, char_first_gen)

                pos_b_item = {
                    "sub_idx": b_idx,
                    "read_option_ids": oids_in_turn,
                    "read_option_labels": labels_in_turn,
                    "last_option_id": last_oid,
                    "last_option_label": last_olabel,
                    "turn_summary_label": turn_label,
                    "tok_idx": tok_think_nl,           # Primary: \n after <think> (generation prompt end)
                    "tok_idx_first_gen": tok_first_gen, # Alt 1: first generated content token in <think>
                    "tok_idx_im_start": tok_im_start,   # Alt 2: <|im_start|> token
                }
                pos_b_list.append(pos_b_item)
                option_label_counts_b[last_olabel] += 1
                stats["total_pos_b"] += 1

                index_rows.append([
                    run_id, sample_id, scenario_id, variant, epoch, cond, int(is_tuning),
                    "pos_b", b_idx, last_oid, last_olabel,
                    tok_think_nl, tok_first_gen, tok_im_start, len(full_ids)
                ])
                b_idx += 1

            # --- LOCATE POSITION (c): Action time (token just before option_id in place_order) ---
            pos_c_item = None
            if has_place_order:
                po_pattern = re.compile(
                    r"<function=place_order>\n<parameter=option_id>(\n)([^\n]+)\n</parameter>"
                )
                po_matches = list(po_pattern.finditer(full_text))
                if po_matches:
                    pm = po_matches[-1]
                    chosen_oid = pm.group(2).strip()
                    chosen_label = opt_lookup.get((scenario_id, chosen_oid), "unknown")

                    char_before_oid = pm.start(1)       # \n immediately before option_id
                    char_param_gt = pm.start(1) - 1     # > of <parameter=option_id>
                    char_oid_first = pm.start(2)        # first char of option_id
                    char_oid_last = pm.end(2) - 1       # last char of option_id

                    tok_before_oid = char_to_tok_idx(offsets, char_before_oid)
                    tok_oid_first = char_to_tok_idx(offsets, char_oid_first)
                    tok_oid_last = char_to_tok_idx(offsets, char_oid_last)
                    tok_param_gt = char_to_tok_idx(offsets, char_param_gt)

                    pos_c_item = {
                        "option_id": chosen_oid,
                        "option_label": chosen_label,
                        "tok_idx": tok_before_oid,          # Primary: \n immediately before option_id
                        "tok_idx_oid_first": tok_oid_first, # Alt 1: first token of option_id
                        "tok_idx_oid_last": tok_oid_last,   # Alt 2: last token of option_id
                        "tok_idx_param_gt": tok_param_gt,
                    }
                    option_label_counts_c[chosen_label] += 1
                    stats["total_pos_c"] += 1

                    index_rows.append([
                        run_id, sample_id, scenario_id, variant, epoch, cond, int(is_tuning),
                        "pos_c", 0, chosen_oid, chosen_label,
                        tok_before_oid, tok_oid_first, tok_oid_last, len(full_ids)
                    ])

            rec = {
                "run_id": run_id,
                "sample_id": sample_id,
                "scenario_id": scenario_id,
                "category": scenario_meta.get(scenario_id, {}).get("category", ""),
                "variant": variant,
                "epoch": epoch,
                "prompt_condition": cond,
                "is_tuning": is_tuning,
                "target_call_idx": target_call_idx,
                "total_model_calls": len(evs),
                "has_place_order": has_place_order,
                "logged_input_tokens": logged_input_tokens,
                "rebuilt_input_tokens": len(prompt_ids),
                "input_token_diff": token_diff,
                "total_teacher_forced_tokens": len(full_ids),
                "pos_a": pos_a_list,
                "pos_b": pos_b_list,
                "pos_c": pos_c_item,
            }
            records.append(rec)

            # Collect 5 diverse tuning-scenario runs for visual hand-check in the report
            if (
                is_tuning
                and len(hand_check_examples) < 5
                and has_place_order
                and len(pos_a_list) >= 2
                and len(pos_b_list) >= 1
                and pos_c_item is not None
                and not any(h["scenario_id"] == scenario_id for h in hand_check_examples)
            ):
                hand_check_examples.append({
                    "rec": rec,
                    "scenario_id": scenario_id,
                    "a0_window": format_highlighted_window(
                        tok, full_ids, pos_a_list[0]["tok_idx"], "POS_A[0]"
                    ),
                    "a0_content_window": format_highlighted_window(
                        tok, full_ids, pos_a_list[0]["tok_idx_content_last"], "POS_A_CONTENT[0]"
                    ),
                    "b0_window": format_highlighted_window(
                        tok, full_ids, pos_b_list[0]["tok_idx"], "POS_B[0]"
                    ),
                    "c_window": format_highlighted_window(
                        tok, full_ids, pos_c_item["tok_idx"], "POS_C"
                    ),
                })

    # Write JSONL
    jsonl_path = os.path.join(OUT_DIR, "qwen35_positions_1200.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Write flat CSV index
    csv_path = os.path.join(OUT_DIR, "qwen35_position_index.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([
            "run_id", "sample_id", "scenario_id", "variant", "epoch",
            "prompt_condition", "is_tuning", "pos_type", "sub_idx",
            "option_id", "option_label", "tok_idx", "tok_idx_alt1",
            "tok_idx_alt2", "total_tokens"
        ])
        w.writerows(index_rows)

    # Write Markdown Report
    report_path = os.path.join(OUT_DIR, "T2_POSITION_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("# T2: Token Position Finder Report (Qwen3.5-9B, All 1,200 Runs)\n\n")
        fh.write("## 1. Summary & Fidelity Verification\n\n")
        fh.write(f"- **Total runs processed:** {stats['total_runs']} (600 neutral + 600 ethical)\n")
        fh.write(f"- **Target call input-token exact matches (`len(prompt_ids) == usage.input_tokens`):** **{stats['target_call_exact_match']} / {stats['total_runs']}** (mismatches: {stats['target_call_mismatch']})\n")
        fh.write(f"- **Runs with `place_order` tool call:** {stats['runs_with_place_order']} / {stats['total_runs']} (without order: {stats['runs_without_place_order']})\n")
        fh.write(f"- **Total extracted position entries across 1,200 runs:** {len(index_rows)}\n")
        fh.write(f"  - **Position (a) Per-option (`get_option_details` end):** {stats['total_pos_a']} positions ({stats['total_pos_a']/stats['total_runs']:.2f} per run)\n")
        fh.write(f"    - Harmful options read: {option_label_counts_a['harmful']}\n")
        fh.write(f"    - Safe options read: {option_label_counts_a['safe']}\n")
        fh.write(f"    - Distractor options read: {option_label_counts_a['distractor']}\n")
        fh.write(f"  - **Position (b) Persistence (next assistant turn start):** {stats['total_pos_b']} positions ({stats['total_pos_b']/stats['total_runs']:.2f} per run)\n")
        fh.write(f"    - Preceding last-read option label: harmful={option_label_counts_b['harmful']}, safe={option_label_counts_b['safe']}, distractor={option_label_counts_b['distractor']}\n")
        fh.write(f"  - **Position (c) Action time (`place_order` before `option_id`):** {stats['total_pos_c']} positions\n")
        fh.write(f"    - Chosen option label: harmful={option_label_counts_c['harmful']}, safe={option_label_counts_c['safe']}, distractor={option_label_counts_c['distractor']}, unknown={option_label_counts_c['unknown']}\n\n")

        fh.write("## 2. Exact Token Definitions in Qwen3.5-9B Chat Template\n\n")
        fh.write("| Position | Primary `tok_idx` | `tok_idx_alt1` | `tok_idx_alt2` | Template Context |\n")
        fh.write("|---|---|---|---|---|\n")
        fh.write("| **(a) Per-option (`pos_a`)** | `</tool_response>` closing token (`id=248067`) of each `get_option_details` block | Last content token of the listing (before `\\n</tool_response>`) | `\\n` token (`id=198`) immediately before `</tool_response>` | `...Tags: ...\\n</tool_response>` |\n")
        fh.write("| **(b) Persistence (`pos_b`)** | `\\n` token (`id=198`) after `<think>` at the start of the assistant turn (`add_generation_prompt=True` boundary) | First generated content token inside `<think>` | `<|im_start|>` token (`id=248045`) opening the assistant turn | `</tool_response><|im_end|>\\n<|im_start|>assistant\\n<think>\\n[First token]` |\n")
        fh.write("| **(c) Action time (`pos_c`)** | `\\n` token (`id=198`) immediately before the first token of `option_id` inside `place_order` | First token of `option_id` | Last token of `option_id` (before `\\n</parameter>`) | `<function=place_order>\\n<parameter=option_id>\\n[option_id]\\n</parameter>` |\n\n")

        fh.write("## 3. Five Hand-Checked Tuning-Scenario Runs (Highlighted Token Windows)\n\n")
        fh.write("Per the blinding rule (`RQ2_PLAN.md` §9), all 5 hand-checked runs below are drawn exclusively from the 10 tuning scenarios.\n\n")
        for idx, h in enumerate(hand_check_examples, 1):
            r = h["rec"]
            fh.write(f"### Hand-Check Run {idx}: `{r['run_id']}`\n")
            fh.write(f"- **Scenario:** `{r['scenario_id']}` (`{r['category']}`) | **Variant:** `{r['variant']}` | **Epoch:** `{r['epoch']}` | **Condition:** `{r['prompt_condition']}`\n")
            fh.write(f"- **Target Call Index:** `{r['target_call_idx']}` / `{r['total_model_calls'] - 1}` | **Input Tokens:** `{r['logged_input_tokens']}` (rebuilt `{r['rebuilt_input_tokens']}`, diff `{r['input_token_diff']}`) | **Teacher-Forced Tokens:** `{r['total_teacher_forced_tokens']}`\n")
            fh.write(f"- **Pos (a)[0]** (`option_id={r['pos_a'][0]['option_id']}`, `{r['pos_a'][0]['option_label']}`):\n")
            fh.write(f"  - Closing tag (`tok_idx={r['pos_a'][0]['tok_idx']}`): {h['a0_window']}\n")
            fh.write(f"  - Last content token (`tok_idx_content_last={r['pos_a'][0]['tok_idx_content_last']}`): {h['a0_content_window']}\n")
            fh.write(f"- **Pos (b)[0]** (`read_option_ids={r['pos_b'][0]['read_option_ids']}`, `turn_summary={r['pos_b'][0]['turn_summary_label']}`):\n")
            fh.write(f"  - Next turn start (`tok_idx={r['pos_b'][0]['tok_idx']}`): {h['b0_window']}\n")
            fh.write(f"- **Pos (c)** (`chosen_option_id={r['pos_c']['option_id']}`, `{r['pos_c']['option_label']}`):\n")
            fh.write(f"  - Action time before option_id (`tok_idx={r['pos_c']['tok_idx']}`): {h['c_window']}\n\n")

    print("Done! Summary stats:", dict(stats))
    print(f"Wrote {jsonl_path}, {csv_path}, and {report_path}")


if __name__ == "__main__":
    main()
