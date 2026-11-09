# G3: Contrast Probe Training, Controls, & Separation Report

## 1. Probe Performance on Held-Out Contrast `test` Split

| Probe | Estimator | Selected Layer (`val`) | `val` AUROC | Held-Out `test` AUROC | Held-Out `test` Acc |
|---|---|---:|---:|---:|---:|
| **Content Probe** | Mass-Mean | L3 | 0.8272 | **0.8227** | 74.7% |
| **Content Probe** | Logistic Reg (L2) | L26 | 0.9931 | **0.9869** | 93.1% |
| **E1 Evaluation Probe** | Mass-Mean | L1 | 1.0000 | **1.0000** | 100.0% |
| **E1 Evaluation Probe** | Logistic Reg (L2) | L1 | 1.0000 | **1.0000** | 100.0% |
| **E2 Evaluation Probe** | Interaction Mass-Mean | L26 | 0.9169 | **0.9246** | — |
| **Random-Label Control** | Mass-Mean | L1 | 0.5551 | **0.4797** | 48.3% |

## 2. Key Separation Test & Nuisance Orthogonality Checks (`RQ2_PLAN.md` §7)

- **Key Separation Test on E1 `test` pairs (identical harmful listing + identical words *'animal-welfare angle'*):**
  - **E1 Evaluation Probe AUROC on E1 `test`:** `1.0000`
  - **Content Probe AUROC on E1 `test`:** `0.9872`
- **Nuisance Control Cosine Similarities with E1 Evaluation Probe (Requirement: `< 0.30`):**
  - `|cos(w_eval, w_price)|`: `0.1886` (PASS)
  - `|cos(w_eval, w_rating)|`: `0.1236` (PASS)
  - `|cos(w_eval, w_position)|`: `0.1325` (PASS)
