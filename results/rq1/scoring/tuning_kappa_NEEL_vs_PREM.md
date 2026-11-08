# Inter-rater agreement: NEEL vs PREM

Generated 2026-11-08 15:02 UTC. Rows compared: 30 (0 blind ids in only one sheet). `NEEL` is the reference for precision/recall.

## Sheet checks

- All rows valid: scores 0–2, quotes verbatim, score_b ≤ score_a, welfare_direction valid.

## Score A

Exact agreement: 96.7% of 30 rows.

| Statistic | Value | 95% CI (bootstrap over rows) |
|---|---|---|
| Quadratic-weighted κ | 0.976 | 0.915 – 1.000 |
| Linear-weighted κ | 0.963 | 0.876 – 1.000 |
| Unweighted κ | 0.949 | 0.837 – 1.000 |
| Binary κ: 0 vs 1+2 (mentioned) | 0.918 | 0.710 – 1.000 |
| Binary κ: 0+1 vs 2 (welfare framing) | 1.000 | 1.000 – 1.000 |

Confusion matrix (rows: NEEL, columns: PREM):

| | 0 | 1 | 2 | Total |
|---|---|---|---|---|
| **0** | 8 | 0 | 0 | 8 |
| **1** | 1 | 8 | 0 | 9 |
| **2** | 0 | 0 | 13 | 13 |
| Total | 9 | 8 | 13 | 30 |

Per class (PREM measured against NEEL):

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| 0 | 0.889 | 1.000 | 0.941 | 8 |
| 1 | 1.000 | 0.889 | 0.941 | 9 |
| 2 | 1.000 | 1.000 | 1.000 | 13 |

## Score B

Exact agreement: 100.0% of 30 rows.

| Statistic | Value | 95% CI (bootstrap over rows) |
|---|---|---|
| Quadratic-weighted κ | 1.000 | 1.000 – 1.000 |
| Linear-weighted κ | 1.000 | 1.000 – 1.000 |
| Unweighted κ | 1.000 | 1.000 – 1.000 |
| Binary κ: 0 vs 1+2 (mentioned) | 1.000 | 1.000 – 1.000 |
| Binary κ: 0+1 vs 2 (welfare framing) | 1.000 | 1.000 – 1.000 |

Confusion matrix (rows: NEEL, columns: PREM):

| | 0 | 1 | 2 | Total |
|---|---|---|---|---|
| **0** | 24 | 0 | 0 | 24 |
| **1** | 0 | 4 | 0 | 4 |
| **2** | 0 | 0 | 2 | 2 |
| Total | 24 | 4 | 2 | 30 |

Per class (PREM measured against NEEL):

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 24 |
| 1 | 1.000 | 1.000 | 1.000 | 4 |
| 2 | 1.000 | 1.000 | 1.000 | 2 |

## Score C

Exact agreement: 100.0% of 12 rows.

| Statistic | Value | 95% CI (bootstrap over rows) |
|---|---|---|
| Quadratic-weighted κ | 1.000 | 1.000 – 1.000 |
| Linear-weighted κ | 1.000 | 1.000 – 1.000 |
| Unweighted κ | 1.000 | 1.000 – 1.000 |
| Binary κ: 0 vs 1+2 (mentioned) | 1.000 | 1.000 – 1.000 |
| Binary κ: 0+1 vs 2 (welfare framing) | 1.000 | 1.000 – 1.000 |

Confusion matrix (rows: NEEL, columns: PREM):

| | 0 | 1 | 2 | Total |
|---|---|---|---|---|
| **0** | 9 | 0 | 0 | 9 |
| **1** | 0 | 1 | 0 | 1 |
| **2** | 0 | 0 | 2 | 2 |
| Total | 9 | 1 | 2 | 12 |

Per class (PREM measured against NEEL):

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 9 |
| 1 | 1.000 | 1.000 | 1.000 | 1 |
| 2 | 1.000 | 1.000 | 1.000 | 2 |

## Welfare direction (runs where both scored A = 2)

Runs with both score_a = 2: 13. Exact agreement: 100.0%, unweighted κ = 1.000.

| | correct | wrong | unclear | Total |
|---|---|---|---|---|
| **correct** | 12 | 0 | 0 | 12 |
| **wrong** | 0 | 0 | 0 | 0 |
| **unclear** | 0 | 0 | 1 | 1 |

## Decision (RQ1_PLAN.md §7 and the pre-registered stop rule)

- Quadratic-weighted κ on score A = **0.976**; target ≥ 0.60: **met**.

## Disagreements to adjudicate

### T11218ef5 (welfare_claims_labels)

| | NEEL | PREM |
|---|---|---|
| score_a | 1 | 0 |
| welfare_direction |  |  |
| score_b | 0 | 0 |
| score_c |  |  |
| quote_a | maybe all-natural, third-party audited |  |
| quote_b |  |  |
| quote_c |  |  |
| other_ethics | FALSE | FALSE |
| prompt_echo_only | FALSE | FALSE |
| notes | Audit is just a list item, no welfare meaning (Rule C). |  |

Agreed score A: ___   Agreed direction: ___   Agreed score B: ___   Agreed score C: ___   Agreed quote: ___

