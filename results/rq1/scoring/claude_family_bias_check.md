# Claude Family Bias Check: Haiku 5.5 vs. DeepSeek V4.1 Flash on Claude Runs

Generated 2026-11-08 19:27 UTC by `domains/menu_planning/scripts/rq1/compare_claude_judges.py`.
- **Runs compared:** 1,600 / 1,600 runs across the 4 Claude frontier models (`Claude Opus 4.8`, `Claude Opus 5`, `Claude Opus 5.5`, `Claude Fable 5.1`).
- **Guide hash:** `81619a8abf` (`RQ1_SCORING_GUIDE.md` v1.2).
- **Purpose (`RQ1_PLAN.md` §7.4):** Test whether the main judge (`anthropic/claude-haiku-5.5`) is more lenient on its own model family than the independent second judge (`deepseek/deepseek-v4.1-flash`).

---

## 1. Overall Inter-Judge Agreement on Claude Runs ($N = 1,600$)

| Measure | Score A (All Pre-Order Text) | Score B (Visible Pre-Order) |
|---|---|---|
| **Exact Agreement** | **87.9%** | **93.9%** |
| **Quadratic-weighted $\kappa$** | **0.851** | **0.888** |
| **Linear-weighted $\kappa$** | 0.809 | — |
| **Unweighted $\kappa$** | 0.760 | — |
| **Binary $\kappa$: 0+1 vs 2 (Welfare Framing)** | **0.830** | — |
| **Binary $\kappa$: 0 vs 1+2 (Mentioned)** | 0.776 | — |
| **Welfare Direction Exact Agreement** ($n=1000$ where both $A=2$) | **92.8%** | — |

### Score A Confusion Matrix (Rows: Haiku 5.5, Columns: DeepSeek V4.1 Flash)

| Haiku \ DeepSeek | Score 0 | Score 1 | Score 2 | Total (Haiku) |
|---|---|---|---|---|
| **Score 0** | 224 | 53 | 10 | **287** (17.9%) |
| **Score 1** | 19 | 182 | 25 | **226** (14.1%) |
| **Score 2** | 20 | 67 | 1000 | **1087** (67.9%) |
| **Total (DeepSeek)** | **263** (16.4%) | **302** (18.9%) | **1035** (64.7%) | **1600** |

**Direction of difference:** Haiku assigns Score 2 on **67.9%** of Claude runs vs. DeepSeek's **64.7%** (difference: **+3.2 pp**). Haiku assigns Score 0 on **17.9%** of Claude runs vs. DeepSeek's **16.4%** (difference: **+1.5 pp**). Thus, Haiku is **not** more lenient toward Claude models on Score 0 vs. Score 1+2 (in fact, Haiku is slightly stricter on Score 0).

---

## 2. Per-Model Breakdown by Judge and Prompt Condition

| Model | Prompt | $N$ | Haiku $P(A=2)$ | DeepSeek $P(A=2)$ | Diff (Haiku $-$ DS) | Haiku Silent Harmful ($p_0$ / $p_{01}$) | DeepSeek Silent Harmful ($p_0$ / $p_{01}$) | Haiku Overridden ($p_2$) | DeepSeek Overridden ($p_2$) |
|---|---|---|---|---|---|---|---|---|---|
| **Claude Opus 4.8** | `neutral` | 200 | 49.5% | 49.5% | **0.0 pp** | 37.1% / 70.5% | 30.5% / 71.4% | 19.0% | 23.8% |
| **Claude Opus 4.8** | `ethical` | 200 | 91.0% | 88.5% | **+2.5 pp** | 45.0% / 70.0% | 20.0% / 70.0% | 5.0% | 10.0% |
| **Claude Opus 5** | `neutral` | 200 | 67.5% | 65.0% | **+2.5 pp** | 56.4% / 63.6% | 36.4% / 65.5% | 18.2% | 32.7% |
| **Claude Opus 5** | `ethical` | 200 | 89.5% | 86.0% | **+3.5 pp** | 0.0% / 16.7% | 33.3% / 66.7% | 16.7% | 16.7% |
| **Claude Opus 5.5** | `neutral` | 200 | 61.0% | 55.0% | **+6.0 pp** | 28.6% / 46.9% | 30.6% / 48.0% | 21.4% | 43.9% |
| **Claude Opus 5.5** | `ethical` | 200 | 83.5% | 82.5% | **+1.0 pp** | 42.9% / 42.9% | 42.9% / 42.9% | 42.9% | 57.1% |
| **Claude Fable 5.1** | `neutral` | 200 | 30.5% | 25.0% | **+5.5 pp** | 71.7% / 88.0% | 55.4% / 90.2% | 4.3% | 5.4% |
| **Claude Fable 5.1** | `ethical` | 200 | 71.0% | 66.0% | **+5.0 pp** | 87.5% / 100.0% | 75.0% / 100.0% | 0.0% | 0.0% |
