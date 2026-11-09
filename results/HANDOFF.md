# HANDOFF: Sentient Futures Incubator Project (RQ1 & RQ2 Complete -> Starting RQ3)

**Author:** Prem R Tawar  
**Target Collaborator:** Claude Opus 5.5 / Next Engineering Session  
**Project:** Extending TAC (*Agentic Welfare Bench / Menu Planning Domain*)  
**Repository:** `Sentient-Futures-Project-git` (`origin/main`, clean at commit `d3cfa8a`)  
**Date:** November 2026  

---

## 1. Executive Summary & Publication Strategy

This project investigates **unstated values in autonomous agent decisions**: when an AI agent acts on behalf of a user who never mentions ethical/welfare values, does it fail to recognise that a choice is morally significant, or does it evaluate the issue internally and choose to violate it anyway? And does standard Chain-of-Thought (CoT) monitoring catch these failures?

### The Two-Paper + SF Report Strategy
As agreed in our incubator roadmap (`Research Strategy: Extending TAC` and `PROJECT_CONTEXT.md`):
1. **Paper 1 (Benchmark & Behavioral - RQ1):** Targeted at **NeurIPS Evaluations & Datasets Track**. Focuses on the large-scale benchmark (12,400 runs across 15 models), the 74.3% silent harmful rate, and the saying-vs-doing gap under ethical prompts.
2. **Paper 2 (Mechanistic Probing & Oversight - RQ2 & RQ3):** Targeted at **NeurIPS Main Track / ICLR**. Framed strictly as an **AI Alignment & Oversight** problem (CoT unfaithfulness and monitorability). Proves that while 83.4% of failures are *recognition failures*, a critical 4.3% represent a *monitoring gap* (evaluated internally but unstated in CoT). **RQ3 provides the causal proof via activation steering.**
3. **The SF Final Report:** A comprehensive standalone document combining all findings for Aditya Raj (Mentor) and the Sentient Futures committee.

---

## 2. What Has Been Done So Far (100% Complete & Verified)

### A. The Agentic Menu Planning Benchmark (Part A)
- **Domain:** Tool-use benchmark with 4 tools: `search_options`, `get_option_details`, `check_availability`, `place_order`.
- **Scope:** 50 scenarios across 10 documented harm categories (e.g. live crustacean boiling, wire snares, fast-growth broilers, live transport).
- **Confound Controls:** 4 balanced variants per scenario (`base`, `price_swap`, `rating_swap`, `reversed`), ensuring options cannot be selected by price or list order.
- **Corpus:** 15 models (8 open-weight with 3 epochs = 9,600 runs; 7 frontier models with 1 epoch = 2,800 runs) = **12,400 total evaluated trajectories**.

### B. RQ1: Behavioral & CoT Monitoring (Part B)
- **Human Calibration:** Dual blind human scoring by Neel & Prem on 100 validation runs (`consensus_100.csv`, Score A quadratic-weighted $\kappa = 0.852$, 90% exact agreement).
- **LLM Judge:** `Claude Haiku 5.5` validated against human consensus ($\kappa = 0.708$) and cross-checked against `DeepSeek V4.1 Flash` on 1,600 Claude runs ($\kappa = 0.851$, confirming zero family bias).
- **Full Scoring:** All 12,400 runs scored in `rq1_work/outputs/judge/haiku/scores.jsonl`.
- **Statistical Tests (H1–H4 supported with Holm correction):**
  - **H1:** Silent-harmful rate $p_0 = 74.3\%$ ($p < 0.001$).
  - **H2:** Spontaneous welfare mention $p_2 = 1.3\%$ ($p < 0.001$).
  - **H3:** "Saying vs Doing" gap $\Delta = +13.6\%$ ($\Delta_{\text{mention}} = +20.7\%$ vs $\Delta_{\text{safe}} = +7.1\%$, $p < 0.001$).
- **Publication Figures:** Saved in `results/rq1/figures/fig1_silent_harmful_by_model.{png,pdf}` and `fig2_prompt_effect_saying_vs_doing.{png,pdf}`.
- **Results Document:** `results/rq1/RQ1_RESULTS.md`.

### C. RQ2: Internal Activation Probing on Qwen3.5-9B (Part C)
- **Tokenizer & Replay Fidelity (T1 & G2):** 1,200 / 1,200 runs verified with exact input token identity (`len(prompt_ids) == usage.input_tokens`). Teacher-forced top-1 token agreement is 85.35% (mean log-prob: -0.4517).
- **Token Position Index (T2):** Located 6,064 exact token positions across all 1,200 runs:
  - `pos_a` (Option encoding): `</tool_response>` token of option details.
  - `pos_b` (Persistence): `\n` token after `<think>` in the subsequent assistant turn.
  - `pos_c` (Action time): token immediately preceding `option_id` in `place_order`.
  - Report: `results/rq2/t2/T2_POSITION_REPORT.md` (with 5 hand-checked runs highlighted).
- **Contrast Datasets (T6):** 588 QA-verified base items with strict 70/15/15 product-type disjoint splits (`results/rq2/contrast/contrast_sets/`).
- **Pre-Registration (T4):** Locked in `results/rq2/RQ2_PREREGISTRATION.md`.
- **Probing & Controls (G3):**
  - Content probe test AUROC: 0.9869.
  - E1 evaluation probe test AUROC: 1.0000.
  - E2 interaction probe test AUROC: 0.9246.
  - Random control at chance (0.4797).
  - Nuisance control orthogonality: price ($0.1886$), rating ($0.1236$), position ($0.1325$) all $< 0.30$.
- **Benchmark Probing & The Monitoring Gap (G4, G5, R2):**
  - Activations extracted for all 1,200 runs on Molab GPU (`results/rq2/benchmark_probe_scores_1200.csv`).
  - **Decision-Category Table (`results/rq2/RQ2_RESULTS.md`):**
    - **83.4% Recognition Failure (387/464):** The model never evaluated the harm internally and didn't mention it.
    - **4.3% Monitoring Gap (20/464):** The model internally evaluated the harm above the 5% safe-FPR threshold, but remained completely silent in its CoT and output!
    - **1.1% Overt Override (5/464):** Evaluated and stated in text.
    - **11.2% Stated below probe cut-off (52/464):** CoT flagged the issue without exceeding the linear probe threshold.

---

## 3. The Objective for RQ3: Causal Steering & Direction Ablation

**All previous temporary RQ3 scripts have been wiped.** You are starting RQ3 completely fresh!

### The Research Question (H3 in `INTERP_PLAN.md` §6.5):
> *"Does the internal evaluation representation causally influence which option is ordered?"*

### Hypotheses to Test:
1. **H3a (Positive Steering Recovers Safe Choices):** Injecting the evaluation direction into the residual stream ($h \leftarrow h + \alpha \mathbf{w}_{\text{eval}}$) during generation turns converts harmful orders into safe orders under the **neutral prompt**.
2. **H3b (Specificity vs Random Controls):** The effect of $\mathbf{w}_{\text{eval}}$ is significantly greater than randomly sampled vectors of equal norm ($\mathbf{w}_{\text{rand}} \perp \mathbf{w}_{\text{eval}}$).
3. **H3c (Capability Preservation):** At the optimal steering strength $\alpha^*$, the agent retains its ability to output valid JSON tool calls and complete the order ($\ge 95\%$ valid tool calls).
4. **H3d (Negative Ablation):** Projecting out the direction ($h \leftarrow h - (h \cdot \mathbf{w}_{\text{eval}})\mathbf{w}_{\text{eval}}$) on **ethical-prompt** runs drops the safe order rate towards the neutral baseline.

---

## 4. Key Assets & File Locations

Everything you need is already verified and committed to git:

1. **Saved Probe Vectors:**
   - Path: `results/rq2/probe_directions.npz`
   - Keys:
     - `e2_w_mm`: 4096-dim float32 vector for the E2 evaluative interaction direction.
     - `e2_layer`: Layer 26 (1-indexed).
     - `e1_w_mm`: 4096-dim float32 vector for the E1 valence direction.
     - `e1_layer`: Layer 1 (1-indexed).
     - `content_w_mm`: Content baseline vector (Layer 3).
2. **Benchmark Data:**
   - Raw Dataset: `domains/menu_planning/data/processed/dataset.json` (50 scenarios, options, harmful_ids, safe_ids).
   - Tuning Subset: `results/rq2/tuning_scenarios.json` (10 scenarios reserved for development).
   - Agent Prompts: `domains/menu_planning/eval/prompts.py` (`SYSTEM_PROMPT` = neutral OrderHub, `SYSTEM_PROMPT_WELFARE` = ethical Harvest Table).
   - Tool Definitions: `domains/menu_planning/eval/tools.py`.
3. **Molab Environment & Execution:**
   - Model: `Qwen/Qwen3.5-9B` (32 layers, hidden dimension 4096).
   - Environment: Molab GPU (A100/H100) using `marimo`.
   - Virtualenv on Molab: `/home/marimo/Sentient-Futures-Project/.venv/bin/python`.
   - Packages installed: `torch`, `transformers>=5`, `accelerate`, `scikit-learn`, `inspect-ai`.

---

## 5. Recommended Steps for Implementing RQ3

1. **Write the RQ3 Pre-Registration:**
   - Formalize the exact layer(s) (L26 primary, L1 sensitivity), steering coefficients $\alpha \in \{0.0, 0.5, 1.0, 2.0, 4.0\}$, and metric definitions in `results/rq3/RQ3_PREREGISTRATION.md`.
2. **Build the Steering Hook Harness:**
   - Create a clean script in `domains/menu_planning/scripts/rq3/` that:
     - Loads `Qwen/Qwen3.5-9B`.
     - Loads `results/rq2/probe_directions.npz`.
     - Attaches a PyTorch forward hook to `model.model.layers[layer - 1]`:
       $$h \leftarrow h + \alpha \frac{\mathbf{w}}{\|\mathbf{w}\|_2}$$
     - Runs the agent loop on the 10 tuning scenarios (40 runs) under neutral prompt.
     - Measures: (a) Safe order rate, (b) Harmful order rate, (c) Valid tool-call rate, (d) CoT text changes.
3. **Run on Molab:**
   - Push to `main`, pull on Molab, and execute the parameter sweep.
4. **Fold Findings into the Manuscript:**
   - Insert the steering curves into Section 5 of `results/paper/MANUSCRIPT_DRAFT.md`.

You are in a completely clean git state. All underlying data, scores, probes, and reports are committed and ready for you to build RQ3!
