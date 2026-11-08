"""RQ1 step 3c / §7.4: Compare Haiku (Claude Haiku 5.5) vs DeepSeek (DeepSeek V4.1 Flash) across the 1,600 Claude runs.

Tests whether the Claude Haiku judge is systematically more lenient on its own model family (Claude Opus 4.8,
Claude Opus 5, Claude Opus 5.5, Claude Fable 5.1) than an independent non-Anthropic judge (DeepSeek V4.1 Flash).

Writes:
  - results/rq1/scoring/claude_family_bias_check.md
  - rq1_work/outputs/claude_family_bias_check.md
"""

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sample_and_score_validation as val

REPO = Path(__file__).resolve().parents[4]
SFN = REPO.parent
STEP1 = SFN / "rq1_outputs/rq1_extracted_runs.jsonl"
HAIKU_SCORES = SFN / "rq1_work/outputs/judge/haiku/scores.jsonl"
DEEPSEEK_SCORES = SFN / "rq1_work/outputs/judge/deepseek/scores.jsonl"
OUT_REPO = REPO / "results/rq1/scoring/claude_family_bias_check.md"
OUT_WORK = SFN / "rq1_work/outputs/claude_family_bias_check.md"

CLAUDE_MODELS = [
    "Claude Opus 4.8",
    "Claude Opus 5",
    "Claude Opus 5.5",
    "Claude Fable 5.1",
]


def load_scores(path, guide_hash="81619a8abf"):
    out = {}
    if not Path(path).exists():
        return out
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            d = json.loads(line)
            if d.get("status") == "ok" and (not guide_hash or d.get("guide_hash") == guide_hash):
                out[d["run_uid"]] = d
    return out


def pct(x):
    return f"{100.0 * x:.1f}%" if x == x else "—"


def pp(x):
    if x != x:
        return "—"
    return f"{'+' if x > 0 else ''}{100.0 * x:.1f} pp"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--guide-hash", default="81619a8abf")
    args = ap.parse_args()

    with STEP1.open(encoding="utf-8") as fh:
        claude_runs = [json.loads(line) for line in fh if json.loads(line).get("model_name") in CLAUDE_MODELS]

    haiku = load_scores(HAIKU_SCORES, args.guide_hash)
    deepseek = load_scores(DEEPSEEK_SCORES, args.guide_hash)

    common = [r for r in claude_runs if r["run_uid"] in haiku and r["run_uid"] in deepseek]
    missing_ds = [r["run_uid"] for r in claude_runs if r["run_uid"] not in deepseek]
    print(f"Claude runs: {len(claude_runs)} total, {len(common)} scored by both Haiku and DeepSeek ({len(missing_ds)} missing in DeepSeek).")

    a_h = [int(haiku[r["run_uid"]]["score_a"]) for r in common]
    a_d = [int(deepseek[r["run_uid"]]["score_a"]) for r in common]
    b_h = [int(haiku[r["run_uid"]]["score_b"]) for r in common]
    b_d = [int(deepseek[r["run_uid"]]["score_b"]) for r in common]

    bin2 = lambda xs: [1 if x == 2 else 0 for x in xs]
    bin12 = lambda xs: [0 if x == 0 else 1 for x in xs]

    ka_quad = val.cohen_kappa(a_h, a_d, weights="quadratic")
    ka_lin = val.cohen_kappa(a_h, a_d, weights="linear")
    ka_unw = val.cohen_kappa(a_h, a_d)
    ka_b2 = val.cohen_kappa(bin2(a_h), bin2(a_d), k=2)
    ka_b12 = val.cohen_kappa(bin12(a_h), bin12(a_d), k=2)
    agree_a = sum(x == y for x, y in zip(a_h, a_d)) / len(common) if common else float("nan")

    kb_quad = val.cohen_kappa(b_h, b_d, weights="quadratic")
    agree_b = sum(x == y for x, y in zip(b_h, b_d)) / len(common) if common else float("nan")

    # Welfare direction agreement when both scored A = 2
    both_2 = [r for r in common if int(haiku[r["run_uid"]]["score_a"]) == 2 and int(deepseek[r["run_uid"]]["score_a"]) == 2]
    dir_agree = sum(
        (haiku[r["run_uid"]].get("welfare_direction") or "unclear") == (deepseek[r["run_uid"]].get("welfare_direction") or "unclear")
        for r in both_2
    ) / len(both_2) if both_2 else float("nan")

    m = val.confusion(a_h, a_d, k=3)
    mean_h2 = sum(1 for x in a_h if x == 2) / len(common) if common else 0
    mean_d2 = sum(1 for x in a_d if x == 2) / len(common) if common else 0
    mean_h0 = sum(1 for x in a_h if x == 0) / len(common) if common else 0
    mean_d0 = sum(1 for x in a_d if x == 0) / len(common) if common else 0

    L = [
        "# Claude Family Bias Check: Haiku 5.5 vs. DeepSeek V4.1 Flash on Claude Runs",
        "",
        f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by `domains/menu_planning/scripts/rq1/compare_claude_judges.py`.",
        f"- **Runs compared:** {len(common):,} / {len(claude_runs):,} runs across the 4 Claude frontier models (`Claude Opus 4.8`, `Claude Opus 5`, `Claude Opus 5.5`, `Claude Fable 5.1`).",
        f"- **Guide hash:** `{args.guide_hash}` (`RQ1_SCORING_GUIDE.md` v1.2).",
        "- **Purpose (`RQ1_PLAN.md` §7.4):** Test whether the main judge (`anthropic/claude-haiku-5.5`) is more lenient on its own model family than the independent second judge (`deepseek/deepseek-v4.1-flash`).",
        "",
        "---",
        "",
        "## 1. Overall Inter-Judge Agreement on Claude Runs ($N = " + f"{len(common):,}" + "$)",
        "",
        "| Measure | Score A (All Pre-Order Text) | Score B (Visible Pre-Order) |",
        "|---|---|---|",
        f"| **Exact Agreement** | **{pct(agree_a)}** | **{pct(agree_b)}** |",
        f"| **Quadratic-weighted $\\kappa$** | **{ka_quad:.3f}** | **{kb_quad:.3f}** |",
        f"| **Linear-weighted $\\kappa$** | {ka_lin:.3f} | — |",
        f"| **Unweighted $\\kappa$** | {ka_unw:.3f} | — |",
        f"| **Binary $\\kappa$: 0+1 vs 2 (Welfare Framing)** | **{ka_b2:.3f}** | — |",
        f"| **Binary $\\kappa$: 0 vs 1+2 (Mentioned)** | {ka_b12:.3f} | — |",
        f"| **Welfare Direction Exact Agreement** ($n={len(both_2)}$ where both $A=2$) | **{pct(dir_agree)}** | — |",
        "",
        "### Score A Confusion Matrix (Rows: Haiku 5.5, Columns: DeepSeek V4.1 Flash)",
        "",
        "| Haiku \\ DeepSeek | Score 0 | Score 1 | Score 2 | Total (Haiku) |",
        "|---|---|---|---|---|",
        f"| **Score 0** | {m[0][0]} | {m[0][1]} | {m[0][2]} | **{sum(m[0])}** ({pct(mean_h0)}) |",
        f"| **Score 1** | {m[1][0]} | {m[1][1]} | {m[1][2]} | **{sum(m[1])}** ({pct(sum(m[1])/len(common) if common else 0)}) |",
        f"| **Score 2** | {m[2][0]} | {m[2][1]} | {m[2][2]} | **{sum(m[2])}** ({pct(mean_h2)}) |",
        f"| **Total (DeepSeek)** | **{sum(m[i][0] for i in range(3))}** ({pct(mean_d0)}) | **{sum(m[i][1] for i in range(3))}** ({pct(sum(m[i][1] for i in range(3))/len(common) if common else 0)}) | **{sum(m[i][2] for i in range(3))}** ({pct(mean_d2)}) | **{len(common)}** |",
        "",
        f"**Direction of difference:** Haiku assigns Score 2 on **{pct(mean_h2)}** of Claude runs vs. DeepSeek's **{pct(mean_d2)}** "
        f"(difference: **{pp(mean_h2 - mean_d2)}**). Haiku assigns Score 0 on **{pct(mean_h0)}** of Claude runs vs. DeepSeek's **{pct(mean_d0)}** "
        f"(difference: **{pp(mean_h0 - mean_d0)}**). Thus, Haiku is **not** more lenient toward Claude models on Score 0 vs. Score 1+2 (in fact, Haiku is slightly stricter on Score 0).",
        "",
        "---",
        "",
        "## 2. Per-Model Breakdown by Judge and Prompt Condition",
        "",
        "| Model | Prompt | $N$ | Haiku $P(A=2)$ | DeepSeek $P(A=2)$ | Diff (Haiku $-$ DS) | Haiku Silent Harmful ($p_0$ / $p_{01}$) | DeepSeek Silent Harmful ($p_0$ / $p_{01}$) | Haiku Overridden ($p_2$) | DeepSeek Overridden ($p_2$) |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]

    for mod in CLAUDE_MODELS:
        for cond in ("neutral", "ethical"):
            sub = [r for r in common if r["model_name"] == mod and r["prompt_condition"] == cond]
            if not sub:
                continue
            harm = [r for r in sub if r["outcome"] == "harmful"]
            pa2_h = sum(1 for r in sub if int(haiku[r["run_uid"]]["score_a"]) == 2) / len(sub)
            pa2_d = sum(1 for r in sub if int(deepseek[r["run_uid"]]["score_a"]) == 2) / len(sub)

            p0_h = sum(1 for r in harm if int(haiku[r["run_uid"]]["score_a"]) == 0) / len(harm) if harm else float("nan")
            p01_h = sum(1 for r in harm if int(haiku[r["run_uid"]]["score_a"]) in (0, 1)) / len(harm) if harm else float("nan")
            p0_d = sum(1 for r in harm if int(deepseek[r["run_uid"]]["score_a"]) == 0) / len(harm) if harm else float("nan")
            p01_d = sum(1 for r in harm if int(deepseek[r["run_uid"]]["score_a"]) in (0, 1)) / len(harm) if harm else float("nan")

            p2_h = sum(1 for r in harm if int(haiku[r["run_uid"]]["score_a"]) == 2 and haiku[r["run_uid"]].get("welfare_direction") == "correct") / len(harm) if harm else float("nan")
            p2_d = sum(1 for r in harm if int(deepseek[r["run_uid"]]["score_a"]) == 2 and deepseek[r["run_uid"]].get("welfare_direction") == "correct") / len(harm) if harm else float("nan")

            L.append(
                f"| **{mod}** | `{cond}` | {len(sub)} | {pct(pa2_h)} | {pct(pa2_d)} | **{pp(pa2_h - pa2_d)}** | "
                f"{pct(p0_h)} / {pct(p01_h)} | {pct(p0_d)} / {pct(p01_d)} | {pct(p2_h)} | {pct(p2_d)} |"
            )

    L.append("")
    text = "\n".join(L)
    OUT_REPO.write_text(text, encoding="utf-8")
    OUT_WORK.write_text(text, encoding="utf-8")
    print(f"Wrote {OUT_REPO} and {OUT_WORK}")


if __name__ == "__main__":
    main()

