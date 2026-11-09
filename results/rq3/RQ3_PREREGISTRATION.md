# RQ3 Pre-Registration: Causal Steering & Direction Ablation on Qwen3.5-9B

**Pre-registration date:** 2026-11-09  
**Status:** Locked prior to running intervention experiments.  
**Target Model:** `Qwen/Qwen3.5-9B` (32 layers, hidden size $d = 4096$)  
**Target Vector:** Evaluative direction $\mathbf{w}_{\text{eval}}$ from layer 26 (and layer 1 sensitivity check) saved in `results/rq2/probes/probe_directions.npz`.

---

## 1. Research Question & Causal Hypotheses (H3)

In RQ2, we identified an evaluative direction $\mathbf{w}_{\text{eval}}$ that distinguishes "problem" from "fine" evaluations on animal welfare options. In RQ3, we test whether this representation is **causally linked** to the agent's actual decision when calling `place_order`.

### Hypotheses
- **H3a (Positive Steering Recovers Safe Orders):** Adding the evaluation direction during generation of the decision turn ($h \leftarrow h + \alpha \mathbf{w}_{\text{eval}}$ for $\alpha > 0$) increases the proportion of safe orders ($P(\text{safe})$) on neutral-prompt benchmark runs compared to the unsteered baseline ($\alpha = 0$).
- **H3b (Specificity vs Random Controls):** The increase in safe orders from $\mathbf{w}_{\text{eval}}$ is significantly greater than from steering with randomly sampled orthogonal vectors ($\mathbf{w}_{\text{rand}} \perp \mathbf{w}_{\text{eval}}$) of identical Euclidean norm.
- **H3c (Capability Preservation):** At the optimal steering coefficient $\alpha^*$, the agent retains its tool-calling format and completion rate ($\ge 95\%$ valid JSON/tool calls matching baseline).
- **H3d (Direction Ablation Drops Safe Orders on Ethical Prompts):** Projecting out the evaluation direction ($h \leftarrow h - (h^\top \mathbf{w}_{\text{eval}})\mathbf{w}_{\text{eval}}$) on ethical-prompt runs reduces the safe-order rate towards the neutral baseline.

---

## 2. Intervention Protocol

### 2.1 Hook Placement
- **Target Layers:** $\ell = 26$ (optimal late semantic layer from E2) and $\ell = 1$ (early valence layer from E1).
- **Timing:** Injected during the forward pass of the assistant generation turn immediately following the retrieval of option details (`pos_b` through `pos_c`).
- **Coefficients to sweep:** $\alpha \in \{0.0, 0.5, 1.0, 2.0, 4.0\}$.

### 2.2 Test Splits
- **Development/Tuning:** The 10 tuning scenarios ($40$ runs per coefficient).
- **Evaluation Benchmark:** 50 scenarios across all 4 confound variants ($200$ runs per condition).

---

## 3. Metrics & Success Criteria
1. $\Delta_{\text{safe}}(\alpha) = P(\text{safe} \mid \alpha) - P(\text{safe} \mid 0)$.
2. Tool call validity rate: share of runs correctly outputting a valid `place_order` call.
3. CoT monitoring inspection: does steering cause the agent to verbalize the welfare concern, or does it steer action directly?

