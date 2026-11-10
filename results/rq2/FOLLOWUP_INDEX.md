# RQ2 repairs and follow-up results

These versioned records supplement the preserved original RQ2 outputs. The report ends at RQ2: the behavioural findings remain, but the probes have not established a reliable distinction between welfare evaluation and content or context. No completed causal RQ3 claim is made.

Start with the [full results and discussion draft](../../docs/report_drafts/rq1_rq2_2026-11-10/SF_RQ1_RQ2_results_and_discussion.txt) and [original-plan reconciliation](ORIGINAL_PLAN_RECONCILIATION.txt). The draft includes all follow-up versions, verified numbers, limitations and future research directions. Its HTML companion is available in the same folder for local browser reading.

## Results map

| Bundle | What it contains | Main interpretation |
|---|---|---|
| [repair_v1](repair_v1/REPORT.md) | Initial CPU analysis corrections | Correct aggregation and missingness; superseded by repair_v2 for the repaired benchmark table |
| [repair_v2](repair_v2/STATUS.md) | Targeted 24-forward repair, 225 revised projections, copied inputs and audit trail | Original trajectories were not regenerated; neutral E2 action AUROC remains 0.621, without construct validation |
| [validation_v1](validation_v1/REPORT.md) | Identical-input backend comparison and 120 probe diagnostics | Current numerical agreement passes; default chat rendering and welfare specificity do not |
| [code_audit_v1](code_audit_v1/AUDIT_AND_MINIMUM_PLAN.txt) | E1/E2 formula, position, context and provenance audit | Correct subtraction does not establish transfer or evaluation/content separation |
| [e2_fallback_v1](e2_fallback_v1/README.md) | Review decisions and prospective input contract | Ten pairs required revision; preparation only, not a completed steering pilot |
| [e2_fallback_v2](e2_fallback_v2/SCREEN_RESULT.txt) | 42 checks and reviewed answers | Silent ordering 1/7; welfare answers 13/14, with truncated controls unresolved |
| [e2_pilot_v3](e2_pilot_v3/RESULT_AND_NEXT_STEPS.txt) | 42 forwards and context comparisons | 7/7 with an extra continuation request, 1/7 at tool close; small refit 2/7 |
| [e2_benchmark_v4](e2_benchmark_v4/RESULT_AND_DECISION.txt) | 78 forwards, including 64 states from eight initially fresh pairs | Original E2 baseline 1/8; substantial price/order/context sensitivity |
| [e2_redesign_v5](e2_redesign_v5/RUN_RESULT_AND_DECISION.txt) | 48-state instruction-interaction pilot | Base ordering improves to 6/8; price/order and content concerns remain |
| [e2_factual_v6](e2_factual_v6/RUN_RESULT_AND_DECISION.txt) | 24 new factual states plus reused welfare states | Base AUROC 0.688 with 6/8 pairs; mixed control effects |
| [e2_nuisance_v7](e2_nuisance_v7/LOCAL_FALLBACK_RESULT.txt) | Local nuisance removal from saved states | Price offset shrinks, but discrimination and robustness do not improve |
| [e2_training_design_v8](e2_training_design_v8/PILOT_RESULT.txt) | 192 states from six factorial training pairs | 6/8 in each development condition; not independent validation |
| [e2_scoring_v9](e2_scoring_v9/INTERPRETATION.txt) | One fixed local penalised scorer | Base ordering falls to 4/8; nuisance reductions also remove much of the desired contrast |

The v4 development states are reused in v5–v9. They are eight pairs, not 64 independent examples. The 192 v8 states represent six training pairs. Lower concern does not mean harmless. A failed probe is not evidence that the model lacks welfare understanding.

## Published evidence and exclusions

The repository contains final reports, numerical analyses, frozen job inputs, labels and review provenance, selected activation arrays, small candidate directions, and scientific source. The largest new file is the approximately 6.7 MB v8 input manifest; selected arrays are each approximately 2.1 MB or smaller. These are compact inputs for local analysis, not the full activation archive.

The 1,200-run full caches, multi-layer remote archives, model weights, download ZIPs, access tokens, pairing files, connection logs and temporary transfer scripts are not included. Their local copies were not deleted. Historical reports may mention those external files; this Git commit is not a backup of every full cache or a promise that an old remote session still exists.

The [scientific source archive](../../domains/menu_planning/scripts/rq2/followups/README.md) is located at `domains/menu_planning/scripts/rq2/followups/` from the repository root. Its README explains dependencies, historical path assumptions and safe local checks. The research runner sources are archival evidence; publishing them does not authorise new inference or paid resources.

The original `RQ2_RESULTS.md`, original score table, original probe weights, RQ1 results and original plans are preserved. Use the versioned repaired tables and report discussion for current interpretation. The report's original source-hash register is retained; transient pre-push GitHub-status notes were intentionally omitted.
