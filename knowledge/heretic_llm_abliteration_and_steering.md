# Heretic: Automated LLM Abliteration, Steering & Anti-Slop Weight Engineering

This document provides a comprehensive technical guide to **Heretic** (`p-e-w/heretic` by Philipp Emanuel Weidmann), covering its underlying mathematical architecture, **Arbitrary-Rank Ablation (ARA)**, **Magnitude-Preserving Orthogonal Ablation (MPOA)**, integration with **Optuna TPE Multi-Objective Optimization**, and practical execution for behavioral steering (uncensoring, anti-slop, humor suppression, domain alignment) without post-training or fine-tuning.

---

## 1. Overview & Core Architecture

Heretic is a state-of-the-art framework for automating internal representation modifications in transformer language models:

```mermaid
flowchart TD
    A["Base Model\n(Dense / MoE / Multimodal / Hybrid)"] --> B["Residual Analysis Module\n(Module I/O Hooking & Forward Pass)"]
    C["Good Prompts\n(Harmless / Neutral / Clean Prose)"] --> B
    D["Bad Prompts\n(Harmful / Refusal-Trigger / Slop)"] --> B
    B --> E["Modifier Engine\n(ARA LoRA / MPOA / Projected Abliteration)"]
    E --> F["Optuna TPE Multi-Objective Optimizer\n(Bayesian Parameter Exploration)"]
    F --> G["Evaluator & Scorers\n- KeywordRate (Refusals/Slop)\n- KLDivergence (Original Capabilities)\n- BenchmarkScore (PIQA, MMLU)"]
    G -->|Feedback Loop (Trials 1..100)| F
    F --> H["Pareto-Optimal Steered Model\n(High Compliance, Minimal KL Divergence)"]
    H --> I["Export Pipeline\n(LoRA safetensors / Merged Weights / Hugging Face / GGUF)"]
```

### Core Advantages Over Conventional Ablation:
1. **Fully Automated Multi-Objective Search:** Eliminates manual trial-and-error layer selection by leveraging **Optuna TPESampler** to co-minimize refusal rates and **KL Divergence** against the base model on neutral prompts.
2. **Continuous Layer Direction Interpolation:** Residual directions use floating-point indices with linear interpolation between adjacent layers: $(1 - \alpha) r_i + \alpha r_{i+1}$, opening infinite cross-layer search spaces.
3. **Parametric Kernel Distributions:** Ablation weights follow dynamic parametric curves (`max_weight`, `max_weight_position`, `min_weight`, `min_weight_distance`) configured independently across **Attention Out-Projection** (`o_proj`) and **MLP Down-Projection** (`down_proj`).
4. **Arbitrary-Rank Ablation (ARA - Weidmann 2026):** Optimizes LoRA adapters of rank ~50 via L-BFGS with dual $k$-NN Euclidean distance loss, surpassing traditional rank-1 vector ablation.

---

## 2. Mathematical Foundations & Weight Modification Paradigms

### 2.1. Standard Directional Ablation (Arditi et al. 2024)
Standard ablation computes the refusal direction vector as the difference between mean first-token activations:
$$\vec{r} = \frac{\mu_{\text{bad}} - \mu_{\text{good}}}{\|\mu_{\text{bad}} - \mu_{\text{good}}\|}$$

Target weight matrix $W$ is modified by orthogonalizing it against $\vec{r}$:
$$W' = W - \alpha (W \vec{r}) \vec{r}^T$$

### 2.2. Projected Abliteration & MPOA (Lai 2025)
Naive ablation risks damaging beneficial activation directions. Projected ablation projects out beneficial components prior to modification:
$$\vec{r}_{\text{ortho}} = \vec{r} - (\vec{r} \cdot \vec{g}) \vec{g}, \quad \text{where } \vec{g} = \frac{\mu_{\text{good}}}{\|\mu_{\text{good}}\|}$$

Under **Magnitude-Preserving Orthogonal Ablation (MPOA)**, each row magnitude of the modified weight matrix is renormalized to match the original matrix ($W_{\text{base}}$), preventing performance degradation:
$$W_{\text{eff}} = \text{normalize}(W', p=2, \text{dim}=1) \times \|W_{\text{base}}\|_2$$

### 2.3. Arbitrary-Rank Ablation (ARA - Weidmann 2026)
ARA bypasses single-rank vector limitations by approximating transformations via a rank-$r$ LoRA adapter ($B \times A$, default $r=50$):
$$W_{\text{eff}} = W_{\text{base}} + (B \times A)$$

Guided by the **ARA Loss Function**:
$$\mathcal{L}_{\text{ARA}} = w_{\text{preserve}} \cdot \mathcal{L}_{\text{preserve}} + w_{\text{steer}} \cdot \mathcal{L}_{\text{steer}}$$

Where:
1. **Preserve Good Behavior:** Ensures neutral/harmless prompt activations remain unchanged:
   $$\mathcal{L}_{\text{preserve}} = \frac{1}{N_{\text{good}}} \|y'_{\text{good}} - y_{\text{good}}\|^2$$
2. **Steer Bad Behavior (Dual $k$-NN with Overcorrection):** Pulls unwanted prompt activations toward nearest harmless neighbors while repelling them from original bad activations:
   $$\mathcal{L}_{\text{steer}} = \text{mean}_{i} \left( \frac{1}{k} \sum_{j \in \text{k-NN}(y'_{i, \text{bad}}, y_{\text{good}})} \|y'_{i, \text{bad}} - y_j\| \right) - w_{\text{over}} \cdot \text{mean}_{i} \left( \frac{1}{k} \sum_{j \in \text{k-NN}(y'_{i, \text{bad}}, y_{\text{bad}})} \|y'_{i, \text{bad}} - y_j\| \right)$$

Optimization is executed per-layer via **L-BFGS** with Strong Wolfe line search, achieving surgical behavioral modification without degrading general reasoning capabilities.

---

## 3. Plugin Architecture: Scorers & Modifiers

### 3.1. Modifiers
| Modifier Plugin | Operational Mechanism | Optuna Search Space Parameters |
| :--- | :--- | :--- |
| **`heretic.modifiers.ara.ARA`** | LoRA rank ~50 + L-BFGS with dual $k$-NN Euclidean loss. | `start_layer_index`, `end_layer_index`, `preserve_good_behavior_weight`, `steer_bad_behavior_weight`, `overcorrect_relative_weight`, `neighbor_count`. |
| **`heretic.modifiers.abliteration.Abliteration`** | Orthogonal residual projection with magnitude preservation (MPOA). | `direction_index` (continuous float interpolation), `max_weight`, `max_weight_position`, `min_weight`, `min_weight_distance` (independent for Attention vs MLP). |

### 3.2. Scorers
| Scorer Plugin | Evaluation Objective | Metric Formulation |
| :--- | :--- | :--- |
| **`KeywordRate`** | Measures frequency of refusals, slop, or specific tokens. | Percentage of responses matching target keyword strings (case-insensitive). |
| **`KLDivergence`** | Quantifies token distribution shift from the base model. | $D_{\text{KL}}(P_{\text{base}} \parallel P_{\text{modified}})$ evaluated on harmless test prompts. |
| **`BenchmarkScore`** | Evaluates formal benchmark accuracy via LM Evaluation Harness. | Accuracy across PIQA, MMLU, GSM8K, ARC, and HellaSwag. |

---

## 4. Primary Use Cases

### 4.1. Uncensoring & Refusal Removal (`config.default.toml`)
- **Challenge:** Open-weight models (Gemma 3, Qwen 2.5, Llama 3) frequently reject legitimate security engineering queries (exploit analysis, penetration testing) due to false-positive refusal heuristics.
- **Heretic Solution:** Steers residual refusal vectors toward compliant representations without compromising reasoning integrity.

### 4.2. Weight-Level Anti-Slop Elimination (`config.noslop.toml`)
- **Challenge:** LLMs frequently default to purple prose and repetitive literary clichés:
  * *Eldoria, Lumina, ethereal, celestial, tapestry, bustling, beacon, kaleidoscopic, unyielding, ensnared, testament, deep cosmos, palpable*.
- **Heretic Solution:**
  1. Good prompt pair: *"Write a short story. Avoid literary cliches, purple prose, and flowery language."*
  2. Bad prompt pair: *"Write a short story. Make extensive use of literary cliches, purple prose, and flowery language."*
  3. Scorer detects slop tokens and minimizes them via ARA/MPOA. Model weights are altered permanently to suppress cliché tokens at the probability layer.

### 4.3. Humor Suppression (`config.nohumor.toml`)
- Suppresses forced jokes, puns, and unnecessary emoji spam across conversational tasks.

---

## 5. Hardware Invariants for Dedicated GPU (12 GB+ VRAM)

1. **Models $\le$ 8B Parameters (Qwen 2.5 7B, Llama 3.1 8B):**
   - Run in `bfloat16` with `quantization = "none"`.
   - VRAM Peak: ~9.5 – 11.0 GB.
2. **Models 12B to 14B Parameters (Gemma 3 12B, Qwen 2.5 Coder 14B):**
   - Mandatory 4-bit loading: `quantization = "bnb_4bit"`.
   - On-the-fly dequantization during forward passes while optimizing LoRA adapter $B \times A$.
   - VRAM Peak: ~8.5 – 10.5 GB.
3. **Storage Allocation:**
   - Checkpoints and models reside on Drive F (`<LOCAL_LLM_DIR>
   - OS Drive C writes for model weights are strictly prohibited.
