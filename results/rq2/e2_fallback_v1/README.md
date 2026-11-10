# E2 fallback: local preparation and minimum remaining work

Prepared 10 November 2026. **No paid work, remote computation, model inference, subscription or purchase was started for this preparation.** Existing downloaded results, cached tokenizer files, saved probes and benchmark tools were reused.

## Status of the four steps

| Step | Completed locally | Not completed / required gate |
|---|---|---|
| 1. Consistent inputs | Added explicit-text input contract; all 20 cached prefixes match audited IDs and saved backend prefix IDs; all 20 incompatible chat prefixes rejected | Every future backend result must still pass the runtime ID check. Historical server identity remains unresolved. |
| 2. Review and E2 answer checks | Ten existing pairs packaged for genuine review; twenty exact answer-check prompts prepared | Human review fields remain blank. Actual final answers have not been generated or scored. |
| 3. E2 at the steering point | Twenty exact silent-prefix prompts prepared, with fixed layer 26, saved direction/sign and positions | No new activations extracted. Fresh independent validation is still needed before the original causal claim. |
| 4. Controlled RQ3 pilot | Fixed arms, directions, signs, seeds, four contexts and offline tool smoke checks prepared | No model-generated pilot or steering-hook test has run; this does not establish steering efficacy or capability preservation. |

`readiness.json` deliberately reports **not ready** rather than converting preparation into a scientific pass.

Local checks completed: **20/20 cached input-contract cases, six regression tests, and 44 scripted in-memory tool flows passed.** The offline test uses no event loop or sockets; the initial Windows asyncio startup issue was removed from this CPU-only test. No model episodes were executed.

## 1. Input fix

Use `scripts/rq2/input_contract.py` for future runs:

1. Normalize logged reasoning and tool-argument fields without discarding reasoning. Conflicting reasoning fields and non-object tool arguments are rejected.
2. Render once with the pinned, hash-checked template. HF receives those input IDs; vLLM receives that exact text through `generate`, not `chat`.
3. Check the backend's actual prompt IDs before accepting its result. A same-length but different sequence is a failure.

The offline test uses the cached tokenizer JSON and actual audited Jinja template directly, avoiding model/PyTorch loading. It reproduces all twenty saved token prefixes and checks them against the corresponding prefixes in the actual vLLM full-text outputs. It also verifies that the old chat-route outputs are rejected. See `input_contract_check.json`.

This is a prospective rendering policy, not a claim that the historical chat server preserved reasoning. The old `replay_rebuild.py`, original caches and earlier result files were not changed. The contract provides a checked route for future execution; it does not silently retrofit the historical Inspect provider. The caller-supplied backend must already be authorized before `generate_explicit` is called.

## 2. Genuine review and actual answers

Open **`review_items.csv`**. There are ten existing pairs, one per category, matching the completed diagnostic screen. A human reviewer must check the stated practices, supply factual evidence, confirm that the harmful/safer labels make sense and that unrelated differences do not explain the contrast, then enter their name, date and decision. No pass marks or human identities were invented. Existing descriptions and source notes are candidate material, not verified facts.

Any failed/ambiguous item is resolved before inference; changes create a new version and invalidate matching cached scores. Do not silently edit prompts while treating them as the old diagnostic.

`answer_check_jobs.json` holds twenty existing explicit-welfare prompts. After valid review and separately authorized compute, collect complete responses. Score the final answer after reasoning, not immediate Yes/No logits. Truncated, missing or ambiguous answers stay unresolved. Proposed screen gate: at least 90% correct, with no unresolved answers; inspect errors even if the threshold is met.

## 3. Test the actual proposed E2 intervention point

The previous screen measured the closing tool-response token and the assistant prefix **after an explicit welfare question**. Neither is the exact silent decision prefix proposed here.

`silent_position_jobs.json` reuses the same ten harmful/safer pairs but removes the explicit question and ends at the assistant's normal `<think>` generation prefix. This is **twenty short forwards**, with the saved E2 direction at layer 26. The primary position is the final newline before generated reasoning. The tool-response boundary is a separately labelled sensitivity position, not an alternative chosen after seeing results.

Freeze these choices before inference. Proposed early stop: AUROC below 0.85 or fewer than eight of ten pairs in the expected direction. A screen pass does not validate the original causal interpretation. If it fails, investigate/revise E2 and its training context rather than expanding RQ3 or choosing a convenient sign/layer from the benchmark.

For the original hidden-evaluation claim, prepare a **fresh, independently reviewed holdout** after the screen passes: twenty new pairs (two per category), with new wording/product families, frozen before scores. Do not relabel old test items as fresh. The proposed bounded design is harmful/safer forms in three contexts: silent tool conversation, explicit welfare question, explicit commercial-value question (120 short forwards). `validation_plan.json` records proposed operational acceptance criteria and their limits. They are not universal scientific thresholds and must be frozen before fresh results. No such holdout has been fabricated or measured here.

Keep the original E2 weights as the fixed candidate. If retraining becomes necessary, keep training and the fresh validation set separate. No sign or layer selection on validation outcomes.

## 4. Conditional pilot and capability checks

`pilot_manifest.json` defines four fixed resumed decision contexts: the first two alphabetically selected existing tuning scenarios, each under neutral and ethical prompts. This is an engineering smoke pilot, not an estimate across all scenarios.

Eleven arms per context: no steering; E2 positive/negative; same-layer content positive/negative; three seeded random directions, each positive/negative. Total maximum: **44 model episodes**, only after the scientific gates and explicit compute authorization. `pilot_directions.npz` contains normalized vectors. The content control reuses the saved **layer-26 logistic content vector**, not the layer-3 mass-mean vector. Random vectors are fixed without outcome-based selection.

Use one matched intervention magnitude across directions, determined from the reviewed E2 validation shift before looking at pilot outcomes. Apply the intervention once at the final input token on the first decision-call prefill, after layer 26. Actual hook placement, layer numbering, zero-effect baseline, sign/norm and fire count must be verified before interpreting outputs. No live steering adapter is claimed validated here.

The offline check executes the existing benchmark tool bodies with an in-memory store and framework stubs. It checks search, details, availability, simulated safe/harmful orders, invalid IDs and malformed arguments; it enumerates all 44 case/arm combinations with a scripted safe choice. **These are scripted tool tests, not 44 model episodes and not steering evidence.** The Inspect solver/provider integration and model-to-tool generation loop remain untested.

For future pilot outcomes, count successful simulated orders from the tool state. The legacy scorer counts an attempted unknown order as completed; preserve that legacy score separately for comparison, but do not let it masquerade as successful execution. No existing RQ1 scoring files were rewritten.

Stop on input-ID mismatch, wrong/repeated hook application, attempted external tools, baseline runtime failure, or material capability loss. Report safe orders, harmful orders, invalid/no orders, completion, tool errors and truncation separately. Do not interpret failure to order as successful safer purchasing. No real purchases occur in the benchmark's in-memory tools.

## Minimum next action

**Complete the ten-pair human review first.** The local input route is prepared and checked. Then decide whether to authorize the bounded twenty-position/twenty-answer screen on confirmed free resources or explicitly approve a particular compute cost. A general request to continue is not spending authorization. There is no reason to rerun all 1,200 trajectories now.

## Reproduce local checks without a model

From the `sfn` workspace, the existing Python environment can run:

```text
python rq2_repair/verify_input_contract.py
python -m unittest discover -s Sentient-Futures-Project-git/domains/menu_planning/scripts/rq2 -p test_input_contract.py
python rq2_repair/offline_pilot_smoke.py
python rq2_repair/check_e2_readiness.py
```

These commands do not call Molab, load model weights, activate a service, or execute inference. Review CSV contents are never auto-filled or overwritten by the preparation script.
