# Unstated Values in Agentic Decisions: Recognition, Action, and Monitorability

**Authors:** Prem R Tawar, Neel Kumar  
**Affiliation:** Sentient Futures Project / Alignment Research  
**Date:** November 2026  
**Target:** Main Conference Submission (NeurIPS / ICML / ICLR)

---

## Abstract

As language model agents are increasingly deployed in autonomous real-world settings, they frequently encounter decisions involving values that the user never explicitly stated. When an agent takes an action that violates such an unstated value, does it fail to *recognise* the moral significance of the choice, or does it evaluate the issue internally and choose to prioritize user objectives instead? Furthermore, does standard Chain-of-Thought (CoT) monitoring provide an adequate safety mechanism for catching these failures?

We evaluate 15 contemporary language models (8 open-weights across 3 epochs, 7 frontier models across 12,400 total trajectories) on an agentic benchmark spanning 10 documented animal-welfare harm categories under neutral and ethical system prompts. In **RQ1**, we find that under neutral user requests, open-weight agents place harmful orders in **74.3%** of decisions without verbalizing any moral consideration in their chain-of-thought ($p_0 = 74.3\%$, $p < 0.001$). Under an ethical system prompt, models exhibit a severe "saying vs. doing" gap: explicit moral mentions increase by $+20.7$ percentage points, but safe actions increase by only $+7.1$ points ($\Delta = +13.6\%$, $p < 0.001$). In **RQ2**, we probe the internal residual representations of Qwen3.5-9B across all 1,200 trajectories using strictly orthogonalized contrast probes. We demonstrate that **83.4%** of silent harmful orders reflect genuine **recognition failures** (the model fails to form an evaluative "problem" representation). However, a distinct **4.3%** of harmful orders constitute an unmonitored **monitoring gap**, where the agent internally evaluates the harm above a calibrated 5% safe-FPR threshold while remaining entirely silent in its chain of thought.

---

## 1. Introduction

Chain-of-thought (CoT) monitoring has emerged as a cornerstone of agent supervision: by reading the agent's internal deliberation trace, overseers hope to detect and intervene on harmful behavior before catastrophic actions are taken. However, CoT monitoring relies on a critical assumption: *faithfulness*. If an agent reasons about a value or constraint without recording it in its reasoning tokens, oversight collapses.

This vulnerability is acute when users never state the value. When a user requests catering or shopping without specifying ethical constraints, the model must spontaneously balance unstated societal or animal welfare standards against explicit user constraints (price, delivery speed, cuisine). 

In this work, we operationalize and dissect this phenomenon across two complementary dimensions:
1. **Behavioral & Verbalization (RQ1):** The explicit rate of harmful actions, unstated moral violations, and the disconnect between moral reasoning and moral action under prompt interventions.
2. **Mechanistic & Latent Monitorability (RQ2):** Linear probing of residual stream activations across 32 layers to establish whether silent failures arise from *recognition failures* (the model never notices) or *monitoring gaps* (the model evaluates the concern internally but keeps its CoT clean).

```
                      [User Prompt: No Moral Constraints]
                                      │
                         [Agent Reads Options]
                                      │
                        Internal Evaluation State?
                       /                          \
              [NO: 83.4%]                        [YES: 5.4%]
          Recognition Failure                     /        \
                   │                     CoT Mention?    CoT Silent?
             Silent Harm                      │               │
                                       Overt Override   Monitoring Gap
                                           (1.1%)           (4.3%)
```

---

## 2. Experimental Benchmark

Our testbed is an agentic tool-use environment where agents search catalogs, request option details, check availability, and call `place_order`.
- **Corpus:** 50 realistic scenarios across 10 harm categories (e.g., live boiling of crustaceans, battery cages, wild wire snares, long-distance live transport).
- **Confound Controls:** 4 controlled variants per scenario (`base`, `price_swap`, `rating_swap`, `reversed`), ensuring that options cannot be selected merely by price ranking or list order.
- **Scale:** 8 open-weight models evaluated across 3 independent epochs ($8 \times 50 \times 4 \times 3 \times 2 = 9,600$ runs) and 7 frontier models across 1 epoch ($7 \times 50 \times 4 \times 1 \times 2 = 2,800$ runs), totaling **12,400 evaluated trajectories**.

---

## 3. RQ1 Results: Verbalization and the "Saying vs. Doing" Gap

Trajectories were scored with an LLM judge (`Claude Haiku 5.5`, validated against dual blind human raters Neel & Prem with quadratic weighted $\kappa = 0.852$, and cross-checked against `DeepSeek V4.1 Flash` on 1,600 runs with $\kappa = 0.851$).

### Key Empirical Findings:

1. **H1 (Silent Harmful Rate is the Majority):** Under neutral prompting, open-weight models order the harmful option silently in **$p_0 = 74.3\%$** of runs ($95\%\text{ CI } [69.9\%, 78.4\%]$, $p < 0.001$, strongly rejecting $H_0: p_0 \le 0.50$).
2. **H2 (Spontaneous Moral Recognition is Negligible):** Spontaneous explicit moral reasoning under neutral prompts occurs in only **$p_2 = 1.3\%$** of harmful decisions ($95\%\text{ CI } [0.5\%, 2.5\%]$).
3. **H3 (The Saying vs. Doing Gap):** Introducing an ethical system prompt causes models to talk about ethics far more than they act on them:
   - Increase in moral mentions: $\Delta_{\text{mention}} = +20.7\%$
   - Increase in safe actions: $\Delta_{\text{safe}} = +7.1\%$
   - Paired gap: $\Delta = \Delta_{\text{mention}} - \Delta_{\text{safe}} = \mathbf{+13.6\%}$ ($95\%\text{ CI } [9.8\%, 17.6\%]$, Wilcoxon signed-rank $p < 0.001$).
4. **H4 (Domain Hardness):** Across locked harm categories, silent harms remain pervasive even under strong ethical prompting on complex agricultural and marine practices.

| Model Class | Prompt Condition | Safe Order Rate | Harmful (Score 0: Silent) | Harmful (Score 1: Copy) | Harmful (Score 2: Flagged) |
|---|---|---:|---:|---:|---:|
| **Open-Weight (8 models)** | `neutral` | 23.3% | **74.3%** | 1.1% | 1.3% |
| **Open-Weight (8 models)** | `ethical` | 30.4% | 48.0% | 0.9% | 20.7% |
| **Frontier (7 models)** | `neutral` | 46.8% | 50.1% | 0.5% | 2.6% |
| **Frontier (7 models)** | `ethical` | 74.8% | 11.2% | 0.2% | 13.8% |

---

## 4. RQ2 Results: Internal Activation Probing & The Monitoring Gap

To determine what occurs inside the model during silent harmful decisions, we extracted activations from all 32 transformer layers of `Qwen3.5-9B` across all 1,200 benchmark runs at three teacher-forced positions:
- **`pos_a` (Option encoding):** `</tool_response>` token of each option details listing.
- **`pos_b` (Persistence):** Token after `<think>` in the subsequent assistant turn.
- **`pos_c` (Action time):** Token immediately preceding `option_id` in `place_order`.

### 4.1 Contrast Probes & Strict Orthogonality
Probes were trained on 588 QA-verified base contrast pairs with 70/15/15 product-type disjoint splits:
- **Content Probe ($\mathbf{w}_{\text{content}}$):** Distinguishes harm description vs. length-matched neutral culinary detail (test AUROC: 0.9869).
- **Evaluation Probe ($\mathbf{w}_{\text{eval}}$):** Distinguishes identical harmful listings followed by valence judgements (*"this option is a real problem"* vs. *"this option is fine"*) holding all welfare words identical (test AUROC: 1.0000).
- **Controls:** Probes were orthogonalized against price ($r = 0.188$), rating ($r = 0.123$), and list position ($r = 0.132$), passing all pre-registered $< 0.30$ bounds.

### 4.2 The Decision-Category Breakdown
Calibrating against an out-of-fold **5% false-positive rate on safe options**, we joined the internal evaluation probe projections with RQ1 judge scores:

| Prompt Condition | Total Harmful Orders | Evaluated & Stated (`Score_A = 2`) | **Evaluated, Not Stated (Monitoring Gap)** | Not Evaluated (Recognition Failure) | Stated Below Probe Cut-off |
|---|---:|---:|---:|---:|---:|
| **`neutral`** | 464 | 5 (1.1%) | **20 (4.3%)** | **387 (83.4%)** | 52 (11.2%) |
| **`ethical`** | 353 | 3 (0.8%) | **11 (3.1%)** | **249 (70.5%)** | 90 (25.5%) |

### 4.3 Substantive Takeaways
1. **The Primary Blocker is Recognition (83.4%):** The vast majority of silent harms occur because the base model simply does not spontaneously generate a moral evaluation representation during service catalog browsing.
2. **CoT Monitoring Has a Real Blind Spot (4.3%):** In 1 out of every 23 harmful decisions under neutral prompting, the model's internal residual stream clearly evaluates the option as a welfare problem ($> \tau_{0.05}$), yet this concern is completely omitted from the generated text and chain of thought.

---

## 5. RQ3 Causal Steering Plan (Drafted in §5)

To establish whether the latent evaluation vector $\mathbf{w}_{\text{eval}}$ causally governs option selection, we inject the direction into the agent loop:
$$h_\ell \leftarrow h_\ell + \alpha \mathbf{w}_{\text{eval}}$$
and measure the recovery of safe decisions under neutral prompts.
