# G5: Benchmark Activation Probing Results (Qwen3.5-9B, 1,200 Runs)

## 1. Harmful vs. Safe AUROC by Position and Prompt Condition

10,000-resample scenario-clustered bootstrap over the 50 scenarios (`seed=20261106`).

| Condition | Position | N (Harmful / Safe) | Content Probe AUROC [95% CI] | E1 Eval Probe AUROC [95% CI] | E1 $p$-value | E2 Eval Probe AUROC [95% CI] |
|---|---|---:|---:|---:|---:|---:|
| `neutral` | `pos_a` | 969 / 787 | 0.390 [0.339, 0.442] | **0.398** [0.344, 0.449] | 0.0000 | 0.406 [0.358, 0.455] |
| `neutral` | `pos_b` | 342 / 289 | 0.500 [0.433, 0.564] | **0.530** [0.460, 0.595] | 0.3884 | 0.539 [0.467, 0.606] |
| `neutral` | `pos_c` | 464 / 136 | 0.511 [0.416, 0.592] | **0.518** [0.434, 0.613] | 0.6922 | 0.621 [0.558, 0.685] |
| `ethical` | `pos_a` | 956 / 841 | 0.406 [0.353, 0.462] | **0.422** [0.363, 0.477] | 0.0056 | 0.446 [0.396, 0.493] |
| `ethical` | `pos_b` | 350 / 337 | 0.507 [0.448, 0.570] | **0.494** [0.442, 0.546] | 0.8370 | 0.512 [0.437, 0.584] |
| `ethical` | `pos_c` | 353 / 240 | 0.541 [0.477, 0.604] | **0.549** [0.482, 0.611] | 0.1512 | 0.511 [0.446, 0.580] |

## 2. Split-Half 5% Safe-FPR Calibration (`pos_a`, Neutral)

- **Half A (25 scenarios) 95th-percentile safe threshold ($\tau_A$):** `0.6881`
- **Half B (25 scenarios) 95th-percentile safe threshold ($\tau_B$):** `0.6854`
