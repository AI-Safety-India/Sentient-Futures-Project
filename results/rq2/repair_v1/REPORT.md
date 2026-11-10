# Repaired RQ2 analysis

Exploratory post-audit reanalysis. Original outputs are preserved. These scores do not establish whether moral evaluation occurred.

## Corrected measurement

First reading per run and option; mixed persistence batches excluded; action positions analysed separately. Missing harmful readings stay missing, with no action-score substitution. AUROC intervals use 10,000 scenario-cluster bootstrap resamples (seed 20261106).

| Condition | Position | E1 AUROC | 95% interval |
|---|---|---:|---|
| neutral | first_read | 0.3978 | 0.3432 to 0.4500 |
| neutral | pure_persistence | 0.4600 | 0.2140 to 0.6174 |
| neutral | action | 0.5178 | 0.4329 to 0.6168 |
| ethical | first_read | 0.4231 | 0.3637 to 0.4789 |
| ethical | pure_persistence | 0.4390 | 0.3216 to 0.5593 |
| ethical | action | 0.5486 | 0.4823 to 0.6117 |

## Harmful outcomes at the original option threshold

Thresholds are calibrated on deduplicated neutral safe options in opposite scenario halves. They are not a 5% run-level false-positive guarantee. Above means strictly greater than threshold; below includes equality. Stated means RQ1 Score A equals 2.

| Condition | Above stated | Above unstated | Below unstated | Below stated | Missing reading | Total harmful |
|---|---:|---:|---:|---:|---:|---:|
| neutral | 5 | 20 | 386 | 52 | 1 | 464 |
| ethical | 3 | 11 | 249 | 90 | 0 | 353 |

## Interpretation and remaining checks

The corrected analysis does not rescue E1 as a moral-evaluation detector. Do not interpret below-threshold results as absent recognition or above-threshold unstated results as a proven monitoring gap. E2 action associations remain exploratory.

analysis.json includes 1%, 5% and 10% threshold sensitivities, held-out safe exceedance rates, separate run-maximum-safe calibration, input hashes, paired run comparisons and missingness. Paired comparisons are descriptive, without confidence intervals. Run-max-safe calibration aligns the aggregation operation but does not match the number or context of harmful readings, and does not validate the construct.

Before causal RQ3 interpretation: verify original-call versus final-replay token prefixes and cached layer positions; check matched backend probabilities if available; independently test probe specificity and context transfer. New prompts or corrected prefixes need only targeted new extraction.
