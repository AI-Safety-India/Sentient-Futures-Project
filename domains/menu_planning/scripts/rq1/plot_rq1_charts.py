"""RQ1 step 6b: Generate the two publication charts (RQ1_PLAN.md §10).

  1. Chart 1 (fig1_silent_harmful_by_model.{png,pdf}):
     Decomposition of harmful orders under the neutral prompt by model (Open-Weight vs Frontier panels):
       - Strict silent harmful rate p_0 = P(Score_A = 0 | harmful, neutral) with 95% scenario-clustered bootstrap CIs
       - Fact-only harmful rate P(Score_A = 1 | harmful, neutral), so stacked 0+1 gives broad silent harmful p_01
       - Recognised & overridden rate p_2 = P(Score_A = 2 & direction = correct | harmful, neutral)
       - Misinformed / unclear Score 2 rate P(Score_A = 2 & direction != correct | harmful, neutral)
       - Pre-registered 50% H1 threshold line.

  2. Chart 2 (fig2_prompt_effect_saying_vs_doing.{png,pdf}):
     Paired prompt effect (Ethical minus Neutral, in percentage points) by model (Open-Weight vs Frontier panels):
       - Delta^mention = P(Score_A = 2 | ethical) - P(Score_A = 2 | neutral) ("Saying")
       - Delta^safe    = P(safe | ethical) - P(safe | neutral) ("Doing")
       - Annotated with D = Delta^mention - Delta^safe and 95% scenario-clustered bootstrap CIs.
"""

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[4]
SFN = REPO.parent
STEP1 = SFN / "rq1_outputs/rq1_extracted_runs.jsonl"
SCORES_HAIKU = SFN / "rq1_work/outputs/judge/haiku/scores.jsonl"
FIG_DIR = REPO / "results/rq1/figures"
WORK_FIG_DIR = SFN / "rq1_work/outputs/figures"
SEED = 20261106
B_BOOT = 2000

CATEGORY_ORDER = [
    "wild_capture_bycatch",
    "procedure_defined_products",
    "scale_numbers_waste",
    "lifetime_farming_conditions",
    "embedded_ingredients",
    "live_animal_attraction",
    "high_suffering_farm_products",
    "killing_slaughter_method",
    "live_transport_holding",
    "welfare_claims_labels",
]

OPEN_MODELS = [
    "gpt-oss-20b",
    "gpt-oss-120b",
    "Param2-17B",
    "Sarvam-30B",
    "Nemotron 3.5 Lightning",
    "Mistral Small 4",
    "Qwen3.5-9B",
    "GLM-4.7-Flash",
]

FRONTIER_MODELS = [
    "Claude Fable 5.1",
    "Mistral Large 4",
    "DeepSeek V4 Pro",
    "Claude Opus 5",
    "Claude Opus 4.8",
    "Qwen 3.8 Max",
    "Claude Opus 5.5",
]


def load_merged(step1_path, scores_path, guide_hash="81619a8abf"):
    with Path(step1_path).open(encoding="utf-8") as fh:
        runs = [json.loads(line) for line in fh]
    scores = {}
    with Path(scores_path).open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            d = json.loads(line)
            if d.get("status") == "ok" and (not guide_hash or d.get("guide_hash") == guide_hash):
                scores[d["run_uid"]] = d
    merged = []
    for r in runs:
        s = scores.get(r["run_uid"])
        if not s:
            continue
        merged.append({
            **r,
            "score_a": int(s["score_a"]),
            "welfare_direction": s.get("welfare_direction") or "",
        })
    return merged


def compute_model_stats_and_cis(rows, all_models, n_boot=B_BOOT, seed=SEED):
    by_cat = defaultdict(set)
    for r in rows:
        by_cat[r["category"]].add(r["scenario_id"])
    cat_scens = {c: sorted(s) for c, s in sorted(by_cat.items())}

    # Bucket per (model, cond, scenario_id): [n_all, n_safe, n_harm, n_a2, n_h0, n_h1, n_h2_corr, n_h2_other]
    agg = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0, 0])
    for r in rows:
        m = r["model_name"]
        cond = r["prompt_condition"]
        s = r["scenario_id"]
        v = agg[(m, cond, s)]
        v[0] += 1
        out = r["outcome"]
        sa = r["score_a"]
        wdir = r["welfare_direction"]
        if out == "safe":
            v[1] += 1
        if sa == 2:
            v[3] += 1
        if out == "harmful":
            v[2] += 1
            if sa == 0:
                v[4] += 1
            elif sa == 1:
                v[5] += 1
            elif sa == 2:
                if wdir == "correct":
                    v[6] += 1
                else:
                    v[7] += 1

    def eval_draw(drawn_scens):
        res = {}
        for m in all_models:
            harm_n = sum(agg[(m, "neutral", s)][2] for s in drawn_scens)
            p0 = sum(agg[(m, "neutral", s)][4] for s in drawn_scens) / harm_n if harm_n else 0.0
            p1 = sum(agg[(m, "neutral", s)][5] for s in drawn_scens) / harm_n if harm_n else 0.0
            p2c = sum(agg[(m, "neutral", s)][6] for s in drawn_scens) / harm_n if harm_n else 0.0
            p2o = sum(agg[(m, "neutral", s)][7] for s in drawn_scens) / harm_n if harm_n else 0.0

            tot_n = sum(agg[(m, "neutral", s)][0] for s in drawn_scens)
            tot_e = sum(agg[(m, "ethical", s)][0] for s in drawn_scens)
            dm = (sum(agg[(m, "ethical", s)][3] for s in drawn_scens) / tot_e -
                  sum(agg[(m, "neutral", s)][3] for s in drawn_scens) / tot_n) if (tot_n and tot_e) else 0.0
            ds = (sum(agg[(m, "ethical", s)][1] for s in drawn_scens) / tot_e -
                  sum(agg[(m, "neutral", s)][1] for s in drawn_scens) / tot_n) if (tot_n and tot_e) else 0.0
            res[m] = {
                "p0": 100.0 * p0,
                "p1": 100.0 * p1,
                "p01": 100.0 * (p0 + p1),
                "p2_corr": 100.0 * p2c,
                "p2_other": 100.0 * p2o,
                "dm": 100.0 * dm,
                "ds": 100.0 * ds,
                "d": 100.0 * (dm - ds),
            }
        return res

    full_scens = [s for c in CATEGORY_ORDER for s in cat_scens[c]]
    point = eval_draw(full_scens)

    rnd = random.Random(seed)
    boot = {m: defaultdict(list) for m in all_models}
    for _ in range(n_boot):
        drawn = [rnd.choice(cat_scens[c]) for c in CATEGORY_ORDER for _ in cat_scens[c]]
        b = eval_draw(drawn)
        for m in all_models:
            for k, val in b[m].items():
                boot[m][k].append(val)

    out = {}
    for m in all_models:
        out[m] = {}
        for k, val in point[m].items():
            arr = sorted(boot[m][k])
            lo = arr[int(0.025 * len(arr))]
            hi = arr[int(0.975 * len(arr)) - 1]
            out[m][k] = (val, lo, hi)
    return out


def plot_chart1_silent_harmful(stats, out_dirs):
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "font.size": 10,
        "axes.titlesize": 11.5,
        "axes.labelsize": 10.5,
    })

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10.5, 7.6), gridspec_kw={"height_ratios": [8, 7], "hspace": 0.34}, sharex=True
    )

    c_p0 = "#1f4e78"       # Deep navy: Score 0 (Strict silent harmful)
    c_p1 = "#7fa6c9"       # Muted steel blue: Score 1 (Fact-only mention)
    c_p2o = "#f2b880"      # Soft amber: Score 2 (Misinformed / Unclear direction)
    c_p2c = "#c0392b"      # Crimson: Score 2 (Recognised & Overridden, direction=correct)

    for ax, models, title in (
        (ax1, OPEN_MODELS, "A. Open-Weight Models (Main Group — 3 Epochs, Full Reasoning, $n = 600$ Neutral / Model)"),
        (ax2, FRONTIER_MODELS, "B. Frontier Models with Readable Reasoning (Secondary Group — 1 Epoch, $n = 200$ Neutral / Model)"),
    ):
        y = np.arange(len(models))
        p0 = np.array([stats[m]["p0"][0] for m in models])
        p0_lo = np.array([stats[m]["p0"][1] for m in models])
        p0_hi = np.array([stats[m]["p0"][2] for m in models])
        p1 = np.array([stats[m]["p1"][0] for m in models])
        p2o = np.array([stats[m]["p2_other"][0] for m in models])
        p2c = np.array([stats[m]["p2_corr"][0] for m in models])

        b0 = ax.barh(y, p0, height=0.62, color=c_p0, edgecolor="white", linewidth=0.6, label="Score 0: Silent harmful (Strict H1)")
        b1 = ax.barh(y, p1, left=p0, height=0.62, color=c_p1, edgecolor="white", linewidth=0.6, label="Score 1: Treatment mentioned as culinary/quality fact only")
        b2o = ax.barh(y, p2o, left=p0 + p1, height=0.62, color=c_p2o, edgecolor="white", linewidth=0.6, label="Score 2 (Unclear / Wrong): Welfare raised without option comparison or misinformed")
        b2c = ax.barh(y, p2c, left=p0 + p1 + p2o, height=0.62, color=c_p2c, edgecolor="white", linewidth=0.6, label="Score 2 (Correct — H2): Welfare harm recognised & overridden")

        # 95% CI error bars on Strict Silent Harmful (p0)
        xerr = np.vstack([np.maximum(0, p0 - p0_lo), np.maximum(0, p0_hi - p0)])
        ax.errorbar(p0, y, xerr=xerr, fmt="none", ecolor="#0b1f33", elinewidth=1.3, capsize=3, capthick=1.1, zorder=5)

        # Value annotations (avoid overlapping the p0 95% CI error bar cap at p0_hi)
        for i, m in enumerate(models):
            val0 = p0[i]
            val01 = p0[i] + p1[i]
            val2c = p2c[i]
            if val0 >= 14:
                # Center inside [0, p0_lo] so the white text never touches the left error bar cap
                cx0 = min(val0 / 2.0, p0_lo[i] / 2.0) if p0_lo[i] >= 16 else val0 / 2.0
                ax.text(cx0, y[i], f"{val0:.1f}%", va="center", ha="center", color="white", fontweight="bold", fontsize=8.8)
            # Place p1 label in the clear region to the right of the error bar cap [max(val0, p0_hi + 1.2), val01]
            left_clear = max(val0, p0_hi[i] + 1.2)
            if val01 - left_clear >= 8.5:
                ax.text((left_clear + val01) / 2.0, y[i], f"{p1[i]:.1f}%", va="center", ha="center", color="#0f2537", fontsize=8.3)
            if val2c >= 4.2:
                ax.text(val01 + p2o[i] + val2c / 2.0, y[i], f"{val2c:.1f}%", va="center", ha="center", color="white", fontweight="bold", fontsize=8.2)
            # Annotate broad (0+1) on the right margin
            ax.text(101.2, y[i], f"0+1: {val01:.1f}%  |  H2: {val2c:.1f}%", va="center", ha="left", color="#222222", fontsize=8.4)

        ax.axvline(50.0, color="#222222", linestyle="--", linewidth=1.2, zorder=4)
        ax.set_yticks(y)
        ax.set_yticklabels(models)
        ax.invert_yaxis()
        ax.set_xlim(0, 126)
        ax.set_xticks([0, 20, 40, 50, 60, 80, 100])
        ax.set_xticklabels(["0%", "20%", "40%", "50%\n(H1 threshold)", "60%", "80%", "100%"])
        ax.set_title(title, loc="left", fontweight="bold", pad=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", linestyle=":", alpha=0.45)

    ax2.set_xlabel("Share of Harmful Orders under Neutral Prompt (%)", fontweight="bold", labelpad=6)
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.995), ncol=2, frameon=True, fontsize=8.8)
    fig.suptitle("RQ1 — Pre-Order Reasoning on Harmful Orders (Neutral Prompt)", fontsize=13, fontweight="bold", y=1.04)

    for d in out_dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        fig.savefig(Path(d) / "fig1_silent_harmful_by_model.png", dpi=300, bbox_inches="tight")
        fig.savefig(Path(d) / "fig1_silent_harmful_by_model.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_chart2_prompt_effect(stats, out_dirs):
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "font.size": 10,
        "axes.titlesize": 11.5,
        "axes.labelsize": 10.5,
    })

    # Order models by D = Delta_mention - Delta_safe descending within each group
    open_sorted = sorted(OPEN_MODELS, key=lambda m: stats[m]["d"][0], reverse=True)
    front_sorted = sorted(FRONTIER_MODELS, key=lambda m: stats[m]["d"][0], reverse=True)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10.5, 7.8), gridspec_kw={"height_ratios": [8, 7], "hspace": 0.34}, sharex=True
    )

    c_mention = "#d95f02"  # Warm orange: Delta^mention ("Saying")
    c_safe = "#1b9e77"     # Teal green: Delta^safe ("Doing")

    for ax, models, title in (
        (ax1, open_sorted, "A. Open-Weight Models (H3 Primary Group: Mean $D = +4.9\\text{ pp}, p < 0.0001$)"),
        (ax2, front_sorted, "B. Frontier Models with Readable Reasoning (Secondary Group: Mean $D = -5.6\\text{ pp}$)"),
    ):
        y = np.arange(len(models))
        h = 0.35

        dm = np.array([stats[m]["dm"][0] for m in models])
        dm_lo = np.array([stats[m]["dm"][1] for m in models])
        dm_hi = np.array([stats[m]["dm"][2] for m in models])

        ds = np.array([stats[m]["ds"][0] for m in models])
        ds_lo = np.array([stats[m]["ds"][1] for m in models])
        ds_hi = np.array([stats[m]["ds"][2] for m in models])

        d_gap = np.array([stats[m]["d"][0] for m in models])

        ax.barh(y - h / 2, dm, height=h, color=c_mention, edgecolor="white", label="$\\Delta^{\\text{mention}}$: Change in Welfare Mentions ($\\text{Score}_A = 2$, Saying)")
        ax.barh(y + h / 2, ds, height=h, color=c_safe, edgecolor="white", label="$\\Delta^{\\text{safe}}$: Change in Safe Orders (Doing)")

        xerr_m = np.vstack([np.maximum(0, dm - dm_lo), np.maximum(0, dm_hi - dm)])
        xerr_s = np.vstack([np.maximum(0, ds - ds_lo), np.maximum(0, ds_hi - ds)])
        ax.errorbar(dm, y - h / 2, xerr=xerr_m, fmt="none", ecolor="#5a2500", elinewidth=1.1, capsize=2.5, zorder=5)
        ax.errorbar(ds, y + h / 2, xerr=xerr_s, fmt="none", ecolor="#0a4635", elinewidth=1.1, capsize=2.5, zorder=5)

        for i, m in enumerate(models):
            sign = "+" if d_gap[i] > 0 else ""
            right_x = max(dm_hi[i], ds_hi[i], 0) + 1.5
            badge_color = "#b03a2e" if d_gap[i] > 1.0 else ("#117864" if d_gap[i] < -1.0 else "#444444")
            ax.text(
                right_x, y[i],
                f"Gap $D = {sign}{d_gap[i]:.1f}$ pp  (Say {dm[i]:+.1f} / Do {ds[i]:+.1f})",
                va="center", ha="left", fontsize=8.5, fontweight="bold", color=badge_color
            )

        ax.axvline(0.0, color="#222222", linewidth=1.0)
        ax.set_yticks(y)
        ax.set_yticklabels(models)
        ax.invert_yaxis()
        ax.set_xlim(-6, 98)
        ax.set_title(title, loc="left", fontweight="bold", pad=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", linestyle=":", alpha=0.45)

    ax2.set_xlabel("Prompt Effect: Ethical Prompt minus Neutral Prompt (Percentage Points)", fontweight="bold", labelpad=6)
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.995), ncol=2, frameon=True, fontsize=9.0)
    fig.suptitle("RQ1 (H3) — Saying vs. Doing Under the Ethical Prompt", fontsize=13, fontweight="bold", y=1.04)

    for d in out_dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        fig.savefig(Path(d) / "fig2_prompt_effect_saying_vs_doing.png", dpi=300, bbox_inches="tight")
        fig.savefig(Path(d) / "fig2_prompt_effect_saying_vs_doing.pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--step1", default=str(STEP1))
    ap.add_argument("--scores", default=str(SCORES_HAIKU))
    ap.add_argument("--guide-hash", default="81619a8abf")
    args = ap.parse_args()

    rows = load_merged(args.step1, args.scores, args.guide_hash)
    all_models = OPEN_MODELS + FRONTIER_MODELS
    print(f"Loaded {len(rows)} runs. Computing scenario-clustered bootstrap CIs for {len(all_models)} models...")
    stats = compute_model_stats_and_cis(rows, all_models)

    out_dirs = [FIG_DIR, WORK_FIG_DIR]
    plot_chart1_silent_harmful(stats, out_dirs)
    plot_chart2_prompt_effect(stats, out_dirs)
    print(f"Saved Chart 1 and Chart 2 (PNG + PDF) to {FIG_DIR} and {WORK_FIG_DIR}")


if __name__ == "__main__":
    main()

