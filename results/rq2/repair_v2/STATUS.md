# RQ2 targeted repair completed — 10 November 2026

The paired Molab GPU run completed all 24 planned forward passes. No agent trajectories were regenerated, and original caches and result files were preserved.

## What changed

- **20 runs:** replaced 55 option-reading and 20 persistence snapshots using 21 original-call forwards. Applied their 225 scalar probe projections to a separate, versioned 6,064-row score table. The other 5,989 rows retain their original score strings exactly.
- **Three diagnostic runs:** retained their original activations and scores. All 12 shifted positions agree much more closely with freshly extracted states at the corrected positions than at the stale indices. Corrected those primary indices in the copied metadata and score table. Seven unchanged positions provided comparison controls.
- **No further extraction is required for these specific audit findings.** This is not a blanket validation of the historical backend or probe construct.

The three retained-cache runs are:

- `ethical__kolkata_sunday_lunch_singi_rating_swap__ep3`
- `ethical__madrid_tapas_octopus_supply_contract_base__ep1`
- `ethical__tokyo_friends_themed_brunch_reversed__ep2`

At E2's layer 26, the corrected-position relative L2 discrepancies for the 12 shifted rows are approximately 1.3–5.1%, versus 70.7–119.4% at the stale positions. Corrected-position cosines are at least 0.9986. The seven unchanged controls have approximately 0.9–2.1% relative L2 discrepancies. These are empirical comparisons, not a universal numerical tolerance or a historical fidelity pass. All per-layer comparisons are retained in `repair_audit.json`.

## Result

| First-reading E1 AUROC | Before targeted repair | After targeted repair | Scenario-bootstrap 95% interval |
|---|---:|---:|---|
| Neutral | 0.3978 | 0.3978 | 0.3432–0.4500 |
| Ethical | 0.4231 | 0.4220 | 0.3626–0.4779 |

The option-threshold category counts are unchanged. The extraction repair does not rescue the primary E1 direction as a spontaneous moral-evaluation detector. Do not interpret below-threshold scores as absent recognition, or unstated above-threshold scores as a proven monitoring gap.

## Files and verification

- `inputs/benchmark_probe_scores_1200.csv`: revised scores with explicit activation provenance. `tok_idx` retains the final-replay coordinate for chronology; repaired rows use separate `activation_call_index` and `activation_token_index` fields for the actual extraction coordinates.
- `inputs/t2/qwen35_positions_1200.jsonl`: primary index corrections only. Auxiliary neighbouring positions and historical sequence-length fields were not rewritten; this file is not a standalone manifest for fresh extraction. Use the GPU report's per-job input IDs and indices for replay.
- `repair_audit.json`, `score_changes.csv`: exact changes, original-file hashes and diagnostic comparisons.
- `analysis.json`, `REPORT.md`, `harmful_run_classification.csv`: revised descriptive analysis, 10,000 scenario-bootstrap resamples and threshold sensitivities.
- `archive_verification.json`: remote/local archive SHA-256 agreement, ZIP integrity, tensor shape/finiteness, input-ID hashes and independent local reproduction of all 225 new projections.
- Complete reusable activation archive: `sfn/rq2_repair/rq2_targeted_repair_v1.zip`. It contains the GPU report and 24 NPZ files; originals remain in the six downloaded cache ZIPs.

Model revision: `c202236235762e1c871ad0ccb60c8ee5ba337b9a`; BF16, SDPA; Transformers 5.14.1, PyTorch 2.11.0, NumPy 2.4.6. The historical model revision is still unverified. The environment and audited template hash are recorded in the repair audit.

## Remaining before RQ3

1. Recover historical server-rendered IDs and forced-continuation log probabilities if available. Otherwise the proposed matched Hugging Face/vLLM check tests current implementations; it cannot retroactively prove the original runtime settings. Keep that distinction explicit.
2. Establish genuine human review of the contrast listings; the generated all-pass sheet is not evidence of annotation. Then run a bounded, prespecified context/specificity diagnostic using the saved directions. Do not flip a sign or choose layers from these benchmark outcomes.
3. If the probe remains invalid, report the negative transfer result. RQ3 may be reframed as exploratory steering of a contrast-derived direction, but cannot establish the original recognition-failure or hidden-evaluation claims.
4. Before any RQ3 sweep, verify actual tool execution and outcome scoring, intervention layer/timing, both signs and prompts, norm-matched random/content controls, and capability checks.

No full 1,200-run rerun is indicated by this targeted audit. No new contrast training or RQ3 sweep was started.
