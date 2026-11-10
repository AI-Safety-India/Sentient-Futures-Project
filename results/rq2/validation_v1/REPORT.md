# RQ2 validation decision — 10 November 2026

**Do not proceed to RQ3 as a causal test of the original hidden-moral-evaluation or recognition-failure claims.** The bounded checks are complete. They provide a numerical backend pass on identical inputs, but fail to establish end-to-end chat fidelity or spontaneous-evaluation probe validity.

## Work completed

- Prespecified ten existing test-split listings, one per category, before new scores were measured. Used the saved probe vectors and layers without retraining, sign changes or layer selection.
- Ran 120 short probe forwards: 20 original E1 valence examples, 20 commercial-value valence controls, 40 original E2 question/listing combinations and 40 matched tool-context combinations. Saved all 32 layers at primary positions and, for tool examples, the pre-question reading boundary.
- Ran 20 Hugging Face teacher-forced comparisons and 20 matching vLLM scoring comparisons on existing tuning trajectories. Separately exercised vLLM's chat renderer on each logged-request reconstruction. The one-token outputs needed to invoke that API were not new agent trajectories and were not used as the probability-comparison targets.
- Preserved original RQ2 results. Downloaded and verified the completed activation archive and report hashes. No RQ3 sweep or new probe training was started.

## Backend fidelity: numerical pass, chat-rendering failure

| Check | Observed result |
|---|---|
| Full replay text tokenized by vLLM versus Hugging Face | Exact IDs in 20/20 runs |
| Teacher-forced continuation tokens compared | 10,471 |
| Pooled log-probability correlation | 0.999703 |
| Lowest per-run correlation | 0.999257 |
| Mean absolute log-probability difference | 0.01171 nats |
| Largest absolute log-probability difference | 0.36656 nats |
| vLLM chat-rendered prefix versus audited HF-rendered prefix | Exact IDs in 0/20 runs |

The identical-token comparison exceeds the proposed 0.99 correlation criterion globally and in every run. Absolute errors and the largest discrepancies are retained in `backend_fidelity.json`; this is close numerical agreement, not bitwise equivalence.

The ordinary vLLM chat route produces much shorter prefixes. At the first difference, historical assistant reasoning present in the audited HF rendering is absent from the vLLM rendering. Removing `reasoning_content` from the HF messages alone does **not** reproduce the vLLM IDs exactly, so additional message-normalization differences remain. `rendering_diagnostic.json` preserves the actual windows; do not describe this as a fully solved one-field issue.

Both implementations used the same pinned Qwen revision, BF16, PyTorch 2.11.0, Transformers 5.14.1 and NumPy 2.4.6. vLLM 0.24.0 ran in a separate environment with its supported native sampler because Molab's CUDA compiler/header combination could not build the optional FlashInfer sampling extension. This is a **current implementation comparison**. The historical revision, actual historical server-rendered IDs and matched historical log probabilities remain unverified. These results neither certify the old server path nor prove that all original caches need rerunning.

For any future intervention, freeze and test the exact rendering route. An explicitly rendered text route is supported by the present numerical comparison; silently switching it to the default chat route is not equivalent.

## Probe screen: specificity and transfer remain inadequate

AUROC measures harmful/safe separation except for E1 valence rows, where it measures the supplied “problem” versus “fine” statements. These are different tasks and must not be pooled.

| Diagnostic | E1 AUROC | E2 AUROC |
|---|---:|---:|
| Original E1 welfare-polarity sentences | 1.00 | 0.58 |
| Same polarity sentences about commercial value | 1.00 | 0.52 |
| Original E2 context, explicit welfare question | 0.49 | 0.94 |
| Tool context, explicit welfare question | 0.41 | 0.88 |
| Tool context, explicit value question | 0.31 | 0.34 |
| Tool-response reading boundary, before the question | 0.51 | 0.33 |

E1's mean problem-minus-fine shift is approximately 0.132 for welfare and 0.131 for commercial value. It distinguishes explicit polarity with almost the same strength across domains. This fails to establish welfare-specific evaluation; perfect original contrast performance is insufficient.

E2 retains useful separation **when explicitly asked about welfare**. Its mean harmful-minus-safe shift falls from about 3.87 in the original question context to 1.27 in the tool context. At the unprompted tool-response boundary it is approximately -0.109, with only 1/10 pairs in the expected direction. The pre-question welfare/value copies have the same causal prefix; they are duplicate reading observations, not 20 independent pairs.

This pattern does not validate either direction as a detector of spontaneous hidden moral evaluation. It also does not establish that the model lacks moral recognition. The earlier repaired benchmark result remains E1 AUROC 0.3978 neutral and 0.4220 ethical.

### Limits of this screen

- The ten items came from an already-inspected test set; this is exploratory diagnosis, not a fresh confirmatory holdout.
- Independent human review was not established. `selected_items_review_needed.csv` records the ten items without manufacturing pass marks.
- No explicit-answer accuracy ceiling is claimed: these measurements score internal states, not final answers after reasoning.
- Ten items can expose obvious specificity/transfer failures but cannot certify a successful construct. The item-resampling intervals in `probe_diagnostic.json` are descriptive and do not compensate for this small, non-random, one-per-category selection.

## What can proceed

**Original RQ3 claim: no-go.** Do not use the original RQ2 percentages as validated recognition-failure or hidden-evaluation measurements, and do not call steering along these directions causal confirmation of those quantities.

Two defensible next paths remain:

1. Report RQ2 as a documented measurement/transfer limitation and redesign the probe with genuinely reviewed items, non-welfare polarity controls, held-out wording and product families, and a fresh independent evaluation set. Freeze criteria before observing those new outcomes.
2. Reframe RQ3 as **exploratory steering of a contrast-derived direction**. Before even a pilot, fix the input-rendering contract and smoke-test actual tool execution and order scoring, both intervention signs, matched random/content controls, capability checks, intended layers/timing and both prompts. Success would demonstrate an intervention effect, not prior hidden recognition.

No full 1,200-trajectory rerun is justified automatically by these findings. A new training run, expanded diagnostic or RQ3 experiment should follow a specific revised protocol rather than another unrestricted sweep.

## Evidence

- `protocol.json`: frozen prompts, item-selection rule and backend criteria.
- `probe_diagnostic.json`, `probe_scores.json`: all probe results and descriptive paired-item intervals.
- `backend_fidelity.json`, `backend_runs.csv`: all 20 comparisons and largest token-probability discrepancies.
- `rendering_diagnostic.json`: evidence for the chat-rendering mismatch.
- `artifact_verification.json`: verified archive digest and per-file checks.
- Reusable archive: `sfn/rq2_repair/validation_download/validation_artifacts.zip` (approximately 33.3 MB). It contains activation NPZ files, full input IDs, exact scripts, environment records and raw results. The later rendering diagnostic is saved separately here.

The backend installation and fallback follow the official [vLLM installation guidance](https://docs.vllm.ai/en/latest/getting_started/installation/gpu/) and the installed vLLM 0.24.0 source. The scientific findings above come from the saved project artifacts and these completed runs.
