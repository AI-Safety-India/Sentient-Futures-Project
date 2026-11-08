# Unstated Values in Agentic Decisions: Recognition, Action and Monitorability

**Sentient Futures incubator project, Agentic Welfare Bench (Menu Planning).** Prem R Tawar, Neel Kumar · November 2026

## The problem
AI agents increasingly act for users in settings where the relevant values are never stated. Behaving well then needs two things: **recognising** that a decision is value-relevant, and **acting** on that recognition. A leading oversight proposal is to monitor agents by reading their chain of thought (CoT), but that only works if the considerations that drive a decision appear in the reasoning. For values the user never raises, we don't know which of these fails, or whether reading the reasoning would tell us.

## Research question
> When a language-model agent takes an action that violates a value it was never asked to consider, does it fail to evaluate the relevant consideration as morally significant, or evaluate it and act against it? And does its chain of thought reveal which occurred?

| | Sub-question | Method |
|---|---|---|
| **RQ1** | Does the agent's reasoning mention the welfare consideration? | CoT monitoring (three-level rubric, validated by human raters) |
| **RQ2** | Does the agent internally *evaluate* the harmful option as morally significant, beyond reading its description? | Content probe (baseline) and evaluation probe, with controls |
| **RQ3** | Does that evaluation drive which option it orders? | Steering and direction ablation in a live agent loop |
| **RQ4** | Why does an ethical prompt move some models but not others: values or instruction-following? | Prompt ablation, plus RQ2–RQ3 compared across models |

## Test bed (completed)
An agentic food-ordering benchmark that extends TAC (Brazilek et al., 2026). The user never mentions animals, some options involve documented animal harm, and the final order is scored programmatically.
- **Size:** 50 scenarios × 4 control variants across 10 harm categories.
- **Conditions:** a neutral system prompt and an ethical-brand system prompt.
- **8 open-weight models:** 23–36% safe orders under the neutral prompt. The ethical prompt moves only some of them, for example Qwen3.5-9B by +17 points and gpt-oss-20b by +2.
- **13 frontier models:** 20–91% safe under the neutral prompt and 60–100% under the ethical one.

## Approach
- **Models:**
  - Qwen3.5-9B (main; responsive to the prompt);
  - gpt-oss-20b (contrast; unresponsive);
  - CoT monitoring on all models.
- **Probes:**
  - trained on separate contrast pairs, formatted like the benchmark's tool outputs;
  - read for each option, after reading, and at action time (chosen vs rejected);
  - calibrated with AUROC and a fixed false-positive rate, against the signal when the model is asked about welfare directly.
- **Causal test:** steering and ablation, with random-direction and capability controls.
- **Replay checks:** activations are recorded on the exact contexts the model saw.

## What the results would mean

| Finding | Interpretation |
|---|---|
| Harm evaluated internally, absent from reasoning, harmful order | **Monitoring gap:** reading the CoT misses what was recognised |
| Content encoded, evaluation absent | **Recognition failure:** the agent reads the harm but doesn't evaluate it |
| Evaluated, and steering it changes the choice | The evaluation **drives** behaviour; steering is a candidate fix |
| Evaluated, but steering has no effect | **Prioritisation failure:** represented but not used |

## Contribution
1. Measuring the internal **evaluation**, not only the content, of an unstated value inside multi-turn agentic decisions.
2. A per-decision comparison of **internal evaluation, verbalisation and action**.
3. A mechanistic account of why prompting changes behaviour in some models but not others, controlled for instruction-following.

This builds on CoT-faithfulness and monitorability research, tool-call probing, value steering, and CaML's agentic welfare work.

## Plan
1. CoT judge.
2. Contrast sets.
3. Prompt ablation.
4. Replay pipeline.
5. Probes and calibration.
6. Probe vs CoT analysis.
7. Steering.
8. Replication on gpt-oss-20b.

**Scope:** open-weight models up to about 30B. Out of scope: sparse autoencoders, circuit discovery and fine-tuning.
