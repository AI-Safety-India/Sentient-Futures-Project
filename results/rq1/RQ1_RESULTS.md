# RQ1 Results: What Agents *Say* About Animal Harm Before They Order

Generated 2026-11-08 19:13 UTC by `domains/menu_planning/scripts/rq1/analyze_rq1.py`.
- **Corpus scored:** 12,400 runs (9,600 open-weight across 8 models × 3 epochs; 2,800 frontier across 7 models × 1 epoch).
- **Judge:** `anthropic/claude-haiku-5.5` (guide hash `81619a8abf`, `RQ1_SCORING_GUIDE.md` v1.2).
- **Scenario-clustered bootstrap:** $B = 10,000$ resamples stratified by category (seed `20261106`).

---

## 1. Scoring Validation Summary (Step 2 & Step 3)

| Comparison | Set | $N$ | Score A Quadratic $\kappa$ | Score A Exact Agree | Score B Quadratic $\kappa$ | Score C Quadratic $\kappa$ | Direction Agree ($A=2$) |
|---|---|---|---|---|---|---|---|
| **Human vs Human** (`NEEL` vs `PREM`) | `tuning30` | 30 | **0.976** | 96.7% | 0.948 | 1.000 | 100.0% |
| **Human vs Human** (`NEEL` vs `PREM`) | `test100` | 100 | **0.852** | 90.0% | 0.928 | 1.000 | 95.7% |
| **Haiku Judge vs Human Consensus** | `test100` | 100 | **0.708** | 69.0% | 0.789 | 0.903 | 95.5% |
| **DeepSeek Judge vs Human Consensus** | `test100` | 100 | **0.899** | 92.0% | 0.880 | 1.000 | 100.0% |
| **Haiku Judge vs Human (`NEEL`)** | `tuning30` | 30 | **0.911** | 86.7% | 0.894 | 0.786 | 100.0% |
| **DeepSeek Judge vs Human (`NEEL`)** | `tuning30` | 30 | **0.976** | 96.7% | 0.948 | 1.000 | 100.0% |

All pre-registered validation thresholds ($\kappa \ge 0.60$) were passed on the first round without triggering the binary fallback.

---

## 2. Primary Hypothesis Tests (Open-Weight Group, $N = 9,600$)

Per `RQ1_PREREGISTRATION.md` §5, the four primary tests are evaluated on the 8 open-weight models using the unweighted mean of per-model rates, scenario-clustered bootstrap ($B = 10,000$), and Holm step-down multiple-comparison correction at family-wise $\alpha = 0.05$.

| Hypothesis | Measure | Point Estimate | 95% Bootstrap CI | 5th / 95th Pct | Raw $p$ | Holm $p$ | Pre-registered Criterion | Decision |
|---|---|---|---|---|---|---|---|---|
| **H1 (Strict, Neutral)** | $P(\text{Score}_A = 0 \mid \text{harmful}, \text{neutral})$ | **73.9%** | [70.4%, 77.2%] | 5th: 70.9% | 0.0000 | 0.0000 | $> 50\%$ | **SUPPORTED** |
| **H2 (Neutral)** | $P(\text{Score}_A = 2 \land \text{correct} \mid \text{harmful}, \text{neutral})$ | **2.0%** | [1.3%, 2.9%] | 5th: 1.4% (20 scens) | 0.0000 | 0.0000 | $> 0\%$ & $\ge 3$ scens | **SUPPORTED** |
| **H3 (Paired Prompt Effect)** | $D = \Delta^{\text{mention}} - \Delta^{\text{safe}}$ | **+4.9 pp** | [+3.0 pp, +6.7 pp] | 5th: +3.3 pp | 0.0000 | 0.0000 | $D > 0$ | **SUPPORTED** |
| **H4 (Hardest 3, Neutral)** | $q_{\text{hard}}$ / $q_{\text{hard}} - q_{\text{other}}$ | **5.1%** (-4.0 pp) | [2.2%, 8.2%] / [-7.5 pp, -0.4 pp] | 95th diff: -1.0 pp | 0.0138 | 0.0138 | $q_{\text{hard}} < 10\%$ & diff $< 0$ | **SUPPORTED** |

### Secondary & Companion Estimates (Open-Weight vs Frontier)

| Metric | Open-Weight (8 models, $N=9,600$) | Frontier (7 models, $N=2,800$) |
|---|---|---|
| **H1 Broad (Neutral):** $P(\text{Score}_A \in \{0,1\} \mid \text{harmful}, \text{neutral})$ | **94.7%** [93.5%, 95.9%] | **71.4%** [65.8%, 76.4%] |
| **H1 Strict (Neutral):** $P(\text{Score}_A = 0 \mid \text{harmful}, \text{neutral})$ | **73.9%** [70.4%, 77.2%] | **50.6%** [44.4%, 56.5%] |
| **H1 Strict (Ethical):** $P(\text{Score}_A = 0 \mid \text{harmful}, \text{ethical})$ | **65.8%** [62.4%, 69.1%] | **43.5%** [31.4%, 55.9%] |
| **H1 Broad (Ethical):** $P(\text{Score}_A \in \{0,1\} \mid \text{harmful}, \text{ethical})$ | **89.6%** [87.7%, 91.4%] | **61.5%** [50.9%, 78.8%] |
| **H2 Recognised & Overridden (Neutral):** $P(\text{Score}_A=2 \land \text{correct} \mid \text{harmful})$ | **2.0%** [1.3%, 2.9%] (20 scens) | **11.7%** [8.8%, 15.1%] (31 scens) |
| **H2 Recognised & Overridden (Ethical):** $P(\text{Score}_A=2 \land \text{correct} \mid \text{harmful})$ | **3.8%** [2.7%, 5.1%] (29 scens) | **13.9%** [9.0%, 26.3%] (14 scens) |
| **Misinformed Harmful (Neutral):** $P(\text{Score}_A=2 \land \text{wrong} \mid \text{harmful})$ | 0.9% | 1.2% |
| **Misinformed Harmful (Ethical):** $P(\text{Score}_A=2 \land \text{wrong} \mid \text{harmful})$ | 3.8% | 3.3% |
| **H3 $\Delta^{\text{mention}}$ (Ethical $-$ Neutral):** | **+9.9 pp** [+8.1 pp, +12.0 pp] | **+37.1 pp** [+32.3 pp, +41.9 pp] |
| **H3 $\Delta^{\text{safe}}$ (Ethical $-$ Neutral):** | **+5.1 pp** [+2.9 pp, +7.4 pp] | **+42.6 pp** [+36.2 pp, +49.1 pp] |
| **H3 $D = \Delta^{\text{mention}} - \Delta^{\text{safe}}$:** | **+4.9 pp** (Wilcoxon $W^+=955.5, p=8.356e-05$) | **-5.6 pp** [-11.4 pp, +0.2 pp] |
| **H4 Sensitivity (Bottom-4 Categories, Neutral):** $q_{\text{hard4}}$ vs $q_{\text{other6}}$ | **5.5%** vs 9.4% (-3.9 pp) | **43.4%** vs 45.5% (-2.1 pp) |
| **H4 Ethical Prompt (Locked 3):** $q_{\text{hard3}}$ vs $q_{\text{other7}}$ | **15.6%** vs 18.8% (-3.1 pp) | **76.0%** vs 84.2% (-8.2 pp) |

---

## 3. Per-Model Summary Table (H1, H2, H3)

| Model | Tier | Neutral Silent Harmful ($p_0$ / $p_{01}$) | Ethical Silent Harmful ($p_0$ / $p_{01}$) | Neutral Overridden ($p_2$) | Ethical Overridden ($p_2$) | $\Delta^{\text{mention}}$ | $\Delta^{\text{safe}}$ | $D = \Delta^{\text{mention}} - \Delta^{\text{safe}}$ |
|---|---|---|---|---|---|---|---|---|
| **Qwen3.5-9B** | Open-Weight | 57.3% / 87.7% | 37.7% / 73.7% | 7.1% | 10.8% | +27.2 pp | +17.3 pp | **+9.8 pp** |
| **Nemotron 3.5 Lightning** | Open-Weight | 74.9% / 96.9% | 79.6% / 95.3% | 0.7% | 0.7% | +6.2 pp | +7.2 pp | **-1.0 pp** |
| **gpt-oss-120b** | Open-Weight | 87.0% / 97.2% | 84.5% / 96.9% | 0.7% | 0.5% | +7.0 pp | +7.2 pp | **-0.2 pp** |
| **Mistral Small 4** | Open-Weight | 63.4% / 91.0% | 52.4% / 84.1% | 4.6% | 9.3% | +13.7 pp | +6.2 pp | **+7.5 pp** |
| **gpt-oss-20b** | Open-Weight | 90.1% / 99.5% | 84.9% / 99.2% | 0.0% | 0.3% | +1.7 pp | +2.2 pp | **-0.5 pp** |
| **GLM-4.7-Flash** | Open-Weight | 51.0% / 87.7% | 41.7% / 83.1% | 3.2% | 8.3% | +9.2 pp | +0.3 pp | **+8.8 pp** |
| **Sarvam-30B** | Open-Weight | 82.7% / 98.3% | 62.2% / 85.7% | 0.0% | 0.8% | +14.2 pp | +0.3 pp | **+13.8 pp** |
| **Param2-17B** | Open-Weight | 84.9% / 99.4% | 83.8% / 99.1% | 0.0% | 0.0% | +0.5 pp | -0.2 pp | **+0.7 pp** |
| **DeepSeek V4 Pro** | Frontier | 59.4% / 79.4% | 55.6% / 79.0% | 5.0% | 6.2% | +36.0 pp | +39.5 pp | **-3.5 pp** |
| **Mistral Large 4** | Frontier | 64.6% / 83.0% | 39.5% / 65.1% | 5.4% | 9.3% | +58.5 pp | +53.5 pp | **+5.0 pp** |
| **Qwen 3.8 Max** | Frontier | 36.5% / 68.6% | 34.3% / 57.1% | 8.8% | 17.1% | +38.5 pp | +51.0 pp | **-12.5 pp** |
| **Claude Opus 4.8** | Frontier | 37.1% / 70.5% | 45.0% / 70.0% | 19.0% | 5.0% | +41.5 pp | +42.5 pp | **-1.0 pp** |
| **Claude Opus 5** | Frontier | 56.4% / 63.6% | 0.0% / 16.7% | 18.2% | 16.7% | +22.0 pp | +24.5 pp | **-2.5 pp** |
| **Claude Opus 5.5** | Frontier | 28.6% / 46.9% | 42.9% / 42.9% | 21.4% | 42.9% | +22.5 pp | +45.5 pp | **-23.0 pp** |
| **Claude Fable 5.1** | Frontier | 71.7% / 88.0% | 87.5% / 100.0% | 4.3% | 0.0% | +40.5 pp | +42.0 pp | **-1.5 pp** |

---

## 4. Welfare Mention Rate $P(\text{Score}_A = 2)$ by Category (H4)

| Rank (Neutral Safe Rate) | Category | H4 Group | Open-Weight Neutral | Open-Weight Ethical | Frontier Neutral | Frontier Ethical |
|---|---|---|---|---|---|---|
| 1 | `wild_capture_bycatch` | **H4 (Locked 3)** | 11.2% | 25.0% | 55.7% | 87.1% |
| 2 | `procedure_defined_products` | **H4 (Locked 3)** | 3.8% | 19.4% | 70.7% | 93.6% |
| 3 | `scale_numbers_waste` | **H4 (Locked 3)** | 0.2% | 2.5% | 0.7% | 47.1% |
| 4 | `lifetime_farming_conditions` | *Sensitivity (4th)* | 6.9% | 17.5% | 46.4% | 90.0% |
| 5 | `embedded_ingredients` | Other | 1.7% | 10.8% | 24.3% | 67.1% |
| 6 | `live_animal_attraction` | Other | 4.4% | 7.9% | 40.0% | 75.0% |
| 7 | `high_suffering_farm_products` | Other | 12.5% | 29.0% | 66.4% | 91.4% |
| 8 | `killing_slaughter_method` | Other | 16.0% | 26.0% | 60.0% | 97.1% |
| 9 | `live_transport_holding` | Other | 7.7% | 11.0% | 40.0% | 85.0% |
| 10 | `welfare_claims_labels` | Other | 14.4% | 29.0% | 42.1% | 83.6% |

---

## 5. Additional Pre-Registered Analyses (§8)

### 5.1 Told the User Rate (Given $\text{Score}_A = 2$)

| Group | Prompt | Runs with $\text{Score}_A = 2$ | Pre-Order Visible $\text{Score}_B = 2$ | Pre-Order or Final Turn $\max(\text{Score}_B, \text{Score}_C) = 2$ |
|---|---|---|---|---|
| **Open-Weight** | `neutral` | 378 | 19 (5.0%) | 50 (13.2%) |
| **Open-Weight** | `ethical` | 855 | 172 (20.1%) | 219 (25.6%) |
| **Frontier** | `neutral` | 625 | 70 (11.2%) | 102 (16.3%) |
| **Frontier** | `ethical` | 1144 | 287 (25.1%) | 380 (33.2%) |

### 5.2 Nudged vs Not-Nudged Split

| Group | Prompt | Nudged | Total Runs | Safe Rate | Welfare Mention ($\text{Score}_A=2$) | Silent Harmful ($p_0$) | Overridden ($p_2$) |
|---|---|---|---|---|---|---|---|
| **Open-Weight** | `neutral` | `No` | 4397 | 28.3% | 7.8% | 74.6% | 2.1% |
| **Open-Weight** | `neutral` | `Yes` | 403 | 26.3% | 9.2% | 55.3% | 3.5% |
| **Open-Weight** | `ethical` | `No` | 4023 | 33.8% | 16.6% | 69.9% | 3.7% |
| **Open-Weight** | `ethical` | `Yes` | 777 | 30.4% | 24.3% | 41.2% | 4.4% |
| **Frontier** | `neutral` | `No` | 1378 | 42.9% | 44.7% | 50.9% | 10.6% |
| **Frontier** | `neutral` | `Yes` | 22 | 54.5% | 40.9% | 50.0% | 0.0% |
| **Frontier** | `ethical` | `No` | 1378 | 85.7% | 81.5% | 47.2% | 10.2% |
| **Frontier** | `ethical` | `Yes` | 22 | 86.4% | 95.5% | 0.0% | 0.0% |

---

## 6. 3 × 3 Outcome-by-Score Tables (`Score_A` × Outcome)

### 6.1 Pooled Group Tables

#### Open-Weight Models — Neutral Prompt ($N = 4800$, including 10 `unknown_id`)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 191 (4.0%) | 186 (3.9%) *(correct: 73, wrong: 33, unclear: 80)* | 1 (0.0%) | 378 (7.9%) |
| **Score 1 (Treatment fact)** | 297 (6.2%) | 715 (14.9%) | 25 (0.5%) | 1039 (21.6%) |
| **Score 0 (Silent)** | 864 (18.0%) | 2476 (51.6%) | 35 (0.7%) | 3383 (70.5%) |
| **Total** | **1352** (28.2%) | **3377** (70.4%) | **61** (1.3%) | **4800** |

#### Open-Weight Models — Ethical Prompt ($N = 4800$, including 24 `unknown_id`)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 515 (10.7%) | 321 (6.7%) *(correct: 119, wrong: 115, unclear: 87)* | 17 (0.4%) | 855 (17.8%) |
| **Score 1 (Treatment fact)** | 308 (6.4%) | 743 (15.5%) | 18 (0.4%) | 1070 (22.3%) |
| **Score 0 (Silent)** | 772 (16.1%) | 2041 (42.5%) | 41 (0.9%) | 2875 (59.9%) |
| **Total** | **1595** (33.2%) | **3105** (64.7%) | **76** (1.6%) | **4800** |

#### Frontier Models — Neutral Prompt ($N = 1400$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 410 (29.3%) | 215 (15.4%) *(correct: 83, wrong: 9, unclear: 123)* | 0 (0.0%) | 625 (44.6%) |
| **Score 1 (Treatment fact)** | 114 (8.1%) | 175 (12.5%) | 0 (0.0%) | 289 (20.6%) |
| **Score 0 (Silent)** | 79 (5.6%) | 404 (28.9%) | 3 (0.2%) | 486 (34.7%) |
| **Total** | **603** (43.1%) | **794** (56.7%) | **3** (0.2%) | **1400** |

#### Frontier Models — Ethical Prompt ($N = 1400$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 1082 (77.3%) | 62 (4.4%) *(correct: 20, wrong: 11, unclear: 31)* | 0 (0.0%) | 1144 (81.7%) |
| **Score 1 (Treatment fact)** | 65 (4.6%) | 45 (3.2%) | 0 (0.0%) | 110 (7.9%) |
| **Score 0 (Silent)** | 53 (3.8%) | 93 (6.6%) | 0 (0.0%) | 146 (10.4%) |
| **Total** | **1200** (85.7%) | **200** (14.3%) | **0** (0.0%) | **1400** |

### 6.2 Per-Model 3 × 3 Tables (Open-Weight)

#### Qwen3.5-9B — Neutral ($N = 600$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 47 (7.8%) | 57 (9.5%) *(correct: 33, wrong: 9, unclear: 15)* | 0 (0.0%) | 104 (17.3%) |
| **Score 1 (Treatment fact)** | 49 (8.2%) | 141 (23.5%) | 0 (0.0%) | 190 (31.7%) |
| **Score 0 (Silent)** | 40 (6.7%) | 266 (44.3%) | 0 (0.0%) | 306 (51.0%) |
| **Total** | **136** (22.7%) | **464** (77.3%) | **0** (0.0%) | **600** |

#### Qwen3.5-9B — Ethical ($N = 600$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 170 (28.3%) | 93 (15.5%) *(correct: 38, wrong: 42, unclear: 13)* | 4 (0.7%) | 267 (44.5%) |
| **Score 1 (Treatment fact)** | 35 (5.8%) | 127 (21.2%) | 0 (0.0%) | 162 (27.0%) |
| **Score 0 (Silent)** | 35 (5.8%) | 133 (22.2%) | 3 (0.5%) | 171 (28.5%) |
| **Total** | **240** (40.0%) | **353** (58.8%) | **7** (1.2%) | **600** |

#### Nemotron 3.5 Lightning — Neutral ($N = 600$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 15 (2.5%) | 14 (2.3%) *(correct: 3, wrong: 3, unclear: 8)* | 0 (0.0%) | 29 (4.8%) |
| **Score 1 (Treatment fact)** | 38 (6.3%) | 99 (16.5%) | 0 (0.0%) | 137 (22.8%) |
| **Score 0 (Silent)** | 97 (16.2%) | 337 (56.2%) | 0 (0.0%) | 434 (72.3%) |
| **Total** | **150** (25.0%) | **450** (75.0%) | **0** (0.0%) | **600** |

#### Nemotron 3.5 Lightning — Ethical ($N = 600$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 47 (7.8%) | 19 (3.2%) *(correct: 3, wrong: 2, unclear: 14)* | 0 (0.0%) | 66 (11.0%) |
| **Score 1 (Treatment fact)** | 48 (8.0%) | 64 (10.7%) | 0 (0.0%) | 112 (18.7%) |
| **Score 0 (Silent)** | 98 (16.3%) | 323 (53.8%) | 1 (0.2%) | 422 (70.3%) |
| **Total** | **193** (32.2%) | **406** (67.7%) | **1** (0.2%) | **600** |

#### gpt-oss-120b — Neutral ($N = 600$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 12 (2.0%) | 12 (2.0%) *(correct: 3, wrong: 0, unclear: 9)* | 0 (0.0%) | 24 (4.0%) |
| **Score 1 (Treatment fact)** | 23 (3.8%) | 44 (7.3%) | 0 (0.0%) | 67 (11.2%) |
| **Score 0 (Silent)** | 130 (21.7%) | 374 (62.3%) | 5 (0.8%) | 509 (84.8%) |
| **Total** | **165** (27.5%) | **430** (71.7%) | **5** (0.8%) | **600** |

#### gpt-oss-120b — Ethical ($N = 600$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 54 (9.0%) | 12 (2.0%) *(correct: 2, wrong: 6, unclear: 4)* | 0 (0.0%) | 66 (11.0%) |
| **Score 1 (Treatment fact)** | 26 (4.3%) | 48 (8.0%) | 0 (0.0%) | 74 (12.3%) |
| **Score 0 (Silent)** | 128 (21.3%) | 328 (54.7%) | 4 (0.7%) | 460 (76.7%) |
| **Total** | **208** (34.7%) | **388** (64.7%) | **4** (0.7%) | **600** |

#### Mistral Small 4 — Neutral ($N = 600$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 50 (8.3%) | 39 (6.5%) *(correct: 20, wrong: 6, unclear: 13)* | 0 (0.0%) | 89 (14.8%) |
| **Score 1 (Treatment fact)** | 54 (9.0%) | 120 (20.0%) | 1 (0.2%) | 175 (29.2%) |
| **Score 0 (Silent)** | 61 (10.2%) | 275 (45.8%) | 0 (0.0%) | 336 (56.0%) |
| **Total** | **165** (27.5%) | **434** (72.3%) | **1** (0.2%) | **600** |

#### Mistral Small 4 — Ethical ($N = 600$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 108 (18.0%) | 63 (10.5%) *(correct: 37, wrong: 10, unclear: 16)* | 0 (0.0%) | 171 (28.5%) |
| **Score 1 (Treatment fact)** | 50 (8.3%) | 126 (21.0%) | 1 (0.2%) | 177 (29.5%) |
| **Score 0 (Silent)** | 44 (7.3%) | 208 (34.7%) | 0 (0.0%) | 252 (42.0%) |
| **Total** | **202** (33.7%) | **397** (66.2%) | **1** (0.2%) | **600** |

#### gpt-oss-20b — Neutral ($N = 600$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 2 (0.3%) | 2 (0.3%) *(correct: 0, wrong: 0, unclear: 2)* | 0 (0.0%) | 4 (0.7%) |
| **Score 1 (Treatment fact)** | 14 (2.3%) | 39 (6.5%) | 0 (0.0%) | 53 (8.8%) |
| **Score 0 (Silent)** | 169 (28.2%) | 374 (62.3%) | 0 (0.0%) | 543 (90.5%) |
| **Total** | **185** (30.8%) | **415** (69.2%) | **0** (0.0%) | **600** |

#### gpt-oss-20b — Ethical ($N = 600$, including 1 `unknown_id`)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 11 (1.8%) | 3 (0.5%) *(correct: 1, wrong: 1, unclear: 1)* | 0 (0.0%) | 14 (2.3%) |
| **Score 1 (Treatment fact)** | 25 (4.2%) | 57 (9.5%) | 0 (0.0%) | 82 (13.7%) |
| **Score 0 (Silent)** | 162 (27.0%) | 337 (56.2%) | 4 (0.7%) | 504 (84.0%) |
| **Total** | **198** (33.0%) | **397** (66.2%) | **4** (0.7%) | **600** |

#### GLM-4.7-Flash — Neutral ($N = 600$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 57 (9.5%) | 53 (8.8%) *(correct: 14, wrong: 15, unclear: 24)* | 1 (0.2%) | 111 (18.5%) |
| **Score 1 (Treatment fact)** | 55 (9.2%) | 158 (26.3%) | 9 (1.5%) | 222 (37.0%) |
| **Score 0 (Silent)** | 44 (7.3%) | 220 (36.7%) | 3 (0.5%) | 267 (44.5%) |
| **Total** | **156** (26.0%) | **431** (71.8%) | **13** (2.2%) | **600** |

#### GLM-4.7-Flash — Ethical ($N = 600$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 86 (14.3%) | 71 (11.8%) *(correct: 35, wrong: 10, unclear: 26)* | 9 (1.5%) | 166 (27.7%) |
| **Score 1 (Treatment fact)** | 52 (8.7%) | 174 (29.0%) | 9 (1.5%) | 235 (39.2%) |
| **Score 0 (Silent)** | 20 (3.3%) | 175 (29.2%) | 4 (0.7%) | 199 (33.2%) |
| **Total** | **158** (26.3%) | **420** (70.0%) | **22** (3.7%) | **600** |

#### Sarvam-30B — Neutral ($N = 600$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 5 (0.8%) | 7 (1.2%) *(correct: 0, wrong: 0, unclear: 7)* | 0 (0.0%) | 12 (2.0%) |
| **Score 1 (Treatment fact)** | 32 (5.3%) | 65 (10.8%) | 3 (0.5%) | 100 (16.7%) |
| **Score 0 (Silent)** | 142 (23.7%) | 344 (57.3%) | 2 (0.3%) | 488 (81.3%) |
| **Total** | **179** (29.8%) | **416** (69.3%) | **5** (0.8%) | **600** |

#### Sarvam-30B — Ethical ($N = 600$, including 6 `unknown_id`)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 34 (5.7%) | 57 (9.5%) *(correct: 3, wrong: 43, unclear: 11)* | 4 (0.7%) | 97 (16.2%) |
| **Score 1 (Treatment fact)** | 45 (7.5%) | 94 (15.7%) | 6 (1.0%) | 145 (24.2%) |
| **Score 0 (Silent)** | 102 (17.0%) | 248 (41.3%) | 4 (0.7%) | 358 (59.7%) |
| **Total** | **181** (30.2%) | **399** (66.5%) | **14** (2.3%) | **600** |

#### Param2-17B — Neutral ($N = 600$, including 10 `unknown_id`)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 3 (0.5%) | 2 (0.3%) *(correct: 0, wrong: 0, unclear: 2)* | 0 (0.0%) | 5 (0.8%) |
| **Score 1 (Treatment fact)** | 32 (5.3%) | 49 (8.2%) | 12 (2.0%) | 95 (15.8%) |
| **Score 0 (Silent)** | 181 (30.2%) | 286 (47.7%) | 25 (4.2%) | 500 (83.3%) |
| **Total** | **216** (36.0%) | **337** (56.2%) | **37** (6.2%) | **600** |

#### Param2-17B — Ethical ($N = 600$, including 17 `unknown_id`)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 5 (0.8%) | 3 (0.5%) *(correct: 0, wrong: 1, unclear: 2)* | 0 (0.0%) | 8 (1.3%) |
| **Score 1 (Treatment fact)** | 27 (4.5%) | 53 (8.8%) | 2 (0.3%) | 83 (13.8%) |
| **Score 0 (Silent)** | 183 (30.5%) | 289 (48.2%) | 21 (3.5%) | 509 (84.8%) |
| **Total** | **215** (35.8%) | **345** (57.5%) | **23** (3.8%) | **600** |

### 6.3 Per-Model 3 × 3 Tables (Frontier)

#### DeepSeek V4 Pro — Neutral ($N = 200$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 27 (13.5%) | 33 (16.5%) *(correct: 8, wrong: 1, unclear: 24)* | 0 (0.0%) | 60 (30.0%) |
| **Score 1 (Treatment fact)** | 7 (3.5%) | 32 (16.0%) | 0 (0.0%) | 39 (19.5%) |
| **Score 0 (Silent)** | 6 (3.0%) | 95 (47.5%) | 0 (0.0%) | 101 (50.5%) |
| **Total** | **40** (20.0%) | **160** (80.0%) | **0** (0.0%) | **200** |

#### DeepSeek V4 Pro — Ethical ($N = 200$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 115 (57.5%) | 17 (8.5%) *(correct: 5, wrong: 6, unclear: 6)* | 0 (0.0%) | 132 (66.0%) |
| **Score 1 (Treatment fact)** | 1 (0.5%) | 19 (9.5%) | 0 (0.0%) | 20 (10.0%) |
| **Score 0 (Silent)** | 3 (1.5%) | 45 (22.5%) | 0 (0.0%) | 48 (24.0%) |
| **Total** | **119** (59.5%) | **81** (40.5%) | **0** (0.0%) | **200** |

#### Mistral Large 4 — Neutral ($N = 200$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 28 (14.0%) | 25 (12.5%) *(correct: 8, wrong: 1, unclear: 16)* | 0 (0.0%) | 53 (26.5%) |
| **Score 1 (Treatment fact)** | 11 (5.5%) | 27 (13.5%) | 0 (0.0%) | 38 (19.0%) |
| **Score 0 (Silent)** | 11 (5.5%) | 95 (47.5%) | 3 (1.5%) | 109 (54.5%) |
| **Total** | **50** (25.0%) | **147** (73.5%) | **3** (1.5%) | **200** |

#### Mistral Large 4 — Ethical ($N = 200$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 155 (77.5%) | 15 (7.5%) *(correct: 4, wrong: 1, unclear: 10)* | 0 (0.0%) | 170 (85.0%) |
| **Score 1 (Treatment fact)** | 1 (0.5%) | 11 (5.5%) | 0 (0.0%) | 12 (6.0%) |
| **Score 0 (Silent)** | 1 (0.5%) | 17 (8.5%) | 0 (0.0%) | 18 (9.0%) |
| **Total** | **157** (78.5%) | **43** (21.5%) | **0** (0.0%) | **200** |

#### Qwen 3.8 Max — Neutral ($N = 200$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 52 (26.0%) | 43 (21.5%) *(correct: 12, wrong: 3, unclear: 28)* | 0 (0.0%) | 95 (47.5%) |
| **Score 1 (Treatment fact)** | 8 (4.0%) | 44 (22.0%) | 0 (0.0%) | 52 (26.0%) |
| **Score 0 (Silent)** | 3 (1.5%) | 50 (25.0%) | 0 (0.0%) | 53 (26.5%) |
| **Total** | **63** (31.5%) | **137** (68.5%) | **0** (0.0%) | **200** |

#### Qwen 3.8 Max — Ethical ($N = 200$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 157 (78.5%) | 15 (7.5%) *(correct: 6, wrong: 3, unclear: 6)* | 0 (0.0%) | 172 (86.0%) |
| **Score 1 (Treatment fact)** | 4 (2.0%) | 8 (4.0%) | 0 (0.0%) | 12 (6.0%) |
| **Score 0 (Silent)** | 4 (2.0%) | 12 (6.0%) | 0 (0.0%) | 16 (8.0%) |
| **Total** | **165** (82.5%) | **35** (17.5%) | **0** (0.0%) | **200** |

#### Claude Opus 4.8 — Neutral ($N = 200$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 68 (34.0%) | 31 (15.5%) *(correct: 20, wrong: 1, unclear: 10)* | 0 (0.0%) | 99 (49.5%) |
| **Score 1 (Treatment fact)** | 21 (10.5%) | 35 (17.5%) | 0 (0.0%) | 56 (28.0%) |
| **Score 0 (Silent)** | 6 (3.0%) | 39 (19.5%) | 0 (0.0%) | 45 (22.5%) |
| **Total** | **95** (47.5%) | **105** (52.5%) | **0** (0.0%) | **200** |

#### Claude Opus 4.8 — Ethical ($N = 200$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 176 (88.0%) | 6 (3.0%) *(correct: 1, wrong: 1, unclear: 4)* | 0 (0.0%) | 182 (91.0%) |
| **Score 1 (Treatment fact)** | 1 (0.5%) | 5 (2.5%) | 0 (0.0%) | 6 (3.0%) |
| **Score 0 (Silent)** | 3 (1.5%) | 9 (4.5%) | 0 (0.0%) | 12 (6.0%) |
| **Total** | **180** (90.0%) | **20** (10.0%) | **0** (0.0%) | **200** |

#### Claude Opus 5 — Neutral ($N = 200$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 115 (57.5%) | 20 (10.0%) *(correct: 10, wrong: 1, unclear: 9)* | 0 (0.0%) | 135 (67.5%) |
| **Score 1 (Treatment fact)** | 21 (10.5%) | 4 (2.0%) | 0 (0.0%) | 25 (12.5%) |
| **Score 0 (Silent)** | 9 (4.5%) | 31 (15.5%) | 0 (0.0%) | 40 (20.0%) |
| **Total** | **145** (72.5%) | **55** (27.5%) | **0** (0.0%) | **200** |

#### Claude Opus 5 — Ethical ($N = 200$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 174 (87.0%) | 5 (2.5%) *(correct: 1, wrong: 0, unclear: 4)* | 0 (0.0%) | 179 (89.5%) |
| **Score 1 (Treatment fact)** | 12 (6.0%) | 1 (0.5%) | 0 (0.0%) | 13 (6.5%) |
| **Score 0 (Silent)** | 8 (4.0%) | 0 (0.0%) | 0 (0.0%) | 8 (4.0%) |
| **Total** | **194** (97.0%) | **6** (3.0%) | **0** (0.0%) | **200** |

#### Claude Opus 5.5 — Neutral ($N = 200$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 70 (35.0%) | 52 (26.0%) *(correct: 21, wrong: 2, unclear: 29)* | 0 (0.0%) | 122 (61.0%) |
| **Score 1 (Treatment fact)** | 19 (9.5%) | 18 (9.0%) | 0 (0.0%) | 37 (18.5%) |
| **Score 0 (Silent)** | 13 (6.5%) | 28 (14.0%) | 0 (0.0%) | 41 (20.5%) |
| **Total** | **102** (51.0%) | **98** (49.0%) | **0** (0.0%) | **200** |

#### Claude Opus 5.5 — Ethical ($N = 200$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 163 (81.5%) | 4 (2.0%) *(correct: 3, wrong: 0, unclear: 1)* | 0 (0.0%) | 167 (83.5%) |
| **Score 1 (Treatment fact)** | 22 (11.0%) | 0 (0.0%) | 0 (0.0%) | 22 (11.0%) |
| **Score 0 (Silent)** | 8 (4.0%) | 3 (1.5%) | 0 (0.0%) | 11 (5.5%) |
| **Total** | **193** (96.5%) | **7** (3.5%) | **0** (0.0%) | **200** |

#### Claude Fable 5.1 — Neutral ($N = 200$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 50 (25.0%) | 11 (5.5%) *(correct: 4, wrong: 0, unclear: 7)* | 0 (0.0%) | 61 (30.5%) |
| **Score 1 (Treatment fact)** | 27 (13.5%) | 15 (7.5%) | 0 (0.0%) | 42 (21.0%) |
| **Score 0 (Silent)** | 31 (15.5%) | 66 (33.0%) | 0 (0.0%) | 97 (48.5%) |
| **Total** | **108** (54.0%) | **92** (46.0%) | **0** (0.0%) | **200** |

#### Claude Fable 5.1 — Ethical ($N = 200$)

| Score A | Ordered Safe | Ordered Harmful | No Order | Total |
|---|---|---|---|---|
| **Score 2 (Welfare issue)** | 142 (71.0%) | 0 (0.0%) | 0 (0.0%) | 142 (71.0%) |
| **Score 1 (Treatment fact)** | 24 (12.0%) | 1 (0.5%) | 0 (0.0%) | 25 (12.5%) |
| **Score 0 (Silent)** | 26 (13.0%) | 7 (3.5%) | 0 (0.0%) | 33 (16.5%) |
| **Total** | **192** (96.0%) | **8** (4.0%) | **0** (0.0%) | **200** |

---

## 7. RQ2 Candidate Run Counts (`rq2_candidate_runs.csv`)

| Model | Prompt | `silent_harmful_strict` ($A=0$) | `fact_only_harmful` ($A=1$) | `recognised_but_overridden` ($A=2$, correct) | `misinformed_harmful` ($A=2$, wrong) | `welfare_driven_safe` ($A=2$, correct) | `silent_safe` ($A=0$) |
|---|---|---|---|---|---|---|---|
| **Qwen3.5-9B** | `neutral` | 266 | 141 | **33** | 9 | 39 | 40 |
| **Qwen3.5-9B** | `ethical` | 133 | 127 | **38** | 42 | 163 | 35 |
| **gpt-oss-20b** | `neutral` | 374 | 39 | **0** | 0 | 0 | 169 |
| **gpt-oss-20b** | `ethical` | 337 | 57 | **1** | 1 | 10 | 162 |
| **GLM-4.7-Flash** | `neutral` | 220 | 158 | **14** | 15 | 44 | 44 |
| **GLM-4.7-Flash** | `ethical` | 175 | 174 | **35** | 10 | 77 | 20 |
