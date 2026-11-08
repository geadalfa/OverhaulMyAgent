# Local LLM Engineering & Desktop Ecosystem Guide

## 1. the User's Hardware Profile & Allocation Invariants

| Hardware Component | Exact Specifications | Role & Operational Limits |
| :--- | :--- | :--- |
| **GPU** | **NVIDIA GeForce Dedicated GPU (12 GB+ VRAM) (12 GB GDDR6X)** | *Memory-Bandwidth Bound* (~504 GB/s). Houses primary model weights for fast inference (60–110+ t/s). |
| **CPU** | **AMD Modern Multi-Core Processor (8 Cores, 16 Threads)** | Handles tokenization, context scheduling, and layer offloading during hybrid execution. |
| **System RAM** | **32 GB DDR5** | Memory buffer for larger models (>14B to 35B). Bandwidth ~60 GB/s (~14–25 t/s during partial CPU offload). |
| **Primary Storage** | **Drive F: SSD 2 TB (~365 GB Free)** | **MANDATORY LOCATION:** All AI weights (GGUF, Ollama, AnythingLLM) reside on Drive F (`<LOCAL_AI_DIR>
| **Protected Storage** | **Drive C: SSD OS (~55.7 GB Free)** | **PROHIBITED:** Storing multi-gigabyte models on Drive C to avoid OS partition exhaustion. |

---

## 2. Local Model Hierarchy (Hardware-Matched for Dedicated GPU (12 GB+ VRAM))

### A. Tier 1: Sweet Spot 100% VRAM GPU (~60 – 100+ Tokens/Sec, Zero Latency)
1. **Qwen 2.5 Coder 14B Instruct (Q4_K_M - ~9.2 GB VRAM):**
   * *Specialization:* Code generation, backend reverse-engineering, SQL DDL, and Confluence Mermaid diagramming.
   * *Cloud Parity:* Equivalent to **Claude 3.5 Haiku / GPT-4o (Coding specialized)**.
2. **Gemma 4 12B (Google - ~8.0 GB VRAM):**
   * *Specialization:* Multimodal (text + UI diagrams), balanced general reasoning, long context window.
   * *Cloud Parity:* Equivalent to **Gemini 1.5 Flash / GPT-4o mini**.
3. **DeepSeek-R1-Distill-Qwen-14B (Q4_K_M - ~9.2 GB VRAM):**
   * *Specialization:* Deep reasoning (Chain of Thought / CoT) for edge cases, race conditions, and complex architecture.
   * *Cloud Parity:* Equivalent to **OpenAI o1-mini / Gemini 2.0 Flash Thinking**.
4. **Llama-3.1-Nemotron-Nano-8B-v1 (NVIDIA - ~6.5 GB VRAM in Q8_0):**
   * *Specialization:* Toggleable reasoning mode via `detailed thinking on`, 128K context window.
5. **AJAX 9B (PewDiePie / Odysseus - ~7.5 GB VRAM in Q5_K_M):**
   * *Specialization:* Uncensored daily assistant (0% refusal ablation via Heretic).

### B. Tier 2: Hybrid Tier (12 GB VRAM + 32 GB DDR5 RAM, ~14–25 Tokens/Sec)
1. **Qwen3.8-27B (Apache 2.0 - ~17.7 GB file size):**
   * *Benchmark Highlights:* **Tool Hallucination rate only 0.08%**, SWE-bench Pro 61.7.
   * *Cloud Parity:* Equivalent to **Claude 3.5 Sonnet / GPT-4o**.
   * *Allocation:* ~11 GB VRAM, ~6.7 GB DDR5 RAM.
2. **Nemotron 3.5 Lightning 30B (MoE 3B active):**
   * *Characteristics:* 30B total weights, but only 3B parameters active per token (~35–45 t/s in hybrid mode).
3. **Devstral 24B (Mistral AI):**
   * *Characteristics:* Multi-file repository navigation and large codebase bug fixing.

### C. Tier 3: Server Scale (Exceeds Single Consumer GPU - Out of Memory)
* `openai/gpt-oss-120b` (63.39 GB file -> requires RAM > 70 GB).
* `Kimi K3 (Max)` (2.8T MoE parameter cluster).
* *Recommendation:* Use pay-per-token APIs (SiliconFlow / DeepSeek API) for server-scale needs rather than running locally.

---

## 3. Desktop Workspaces & Agent Harness Ecosystem

| Desktop Workspace | Engine Dependency | Knowledge (RAG) | Rules & Steering | Agent Skills | MCP Support | OS System Control |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AnythingLLM Desktop** | Standalone (Native) | **Tier S (Native LanceDB, Vector RAG)** | Workspace System Prompts | @agent mode: Web, Docs, SQL | Native Client MCP Tools | Sandboxed (Limited via MCP CLI) |
| **Roo Code / Cline (VS Code)** | Ollama / LM Studio | Workspace File Scanning | **Tier S (`.roomodes` & custom rules)** | **Tier S (`execute_command`, `apply_diff`)** | **Tier S (Native MCP Host)** | **Full Direct Control (PowerShell & Files)** |
| **LM Studio Desktop** | Standalone (llama.cpp CUDA) | Basic | System Prompt Presets | None | None | Inference & Local Server Only |
| **Project Odysseus** | Docker + Ollama Stack | Brain Memory + Vector | System Prompt Personas | SearXNG Search & Tools | Configurable | Containerized / Sandboxed |

---

## 4. AnythingLLM & MCP (Model Context Protocol) Integration

### A. AnythingLLM as an MCP Client
AnythingLLM Desktop supports **Model Context Protocol (MCP)** to equip `@agent` modes with external tools:
* **Configuration Path:** *Agent Skills > MCP Servers* (JSON format).
* **Supported Integrations:**
  * **Confluence MCP:** Search, read, and update documentation pages directly.
  * **Bitbucket / GitHub MCP:** Inspect repositories, PRs, diffs, and commit histories.
  * **Database MCP:** Execute SQL schema queries and inspection commands.
  * **NVIDIA App MCP:** Monitor GPU status and local graphics presets.

### B. Operating System Boundaries: AnythingLLM vs VS Code / Antigravity
* **AnythingLLM:** Runs within an application sandbox. Best suited for **PRD/FRD Document RAG, System Architecture Analysis, and Confluence Documentation**.
* **Antigravity / VS Code Roo Code:** Full direct access to PowerShell terminal and filesystem. Best suited for **Autonomous Coding, File Scaffolding, and Local Tooling Builds**.

---

## 5. Local LLM Decensoring, Steering & Ablation (Heretic Engine)

- **Arbitrary-Rank Ablation (ARA):** Uses rank ~50 LoRA adapters optimized via L-BFGS with dual $k$-NN Euclidean distance loss.
- **Magnitude-Preserving Orthogonal Ablation (MPOA):** Renormalizes row magnitudes of modified matrices to match original weights, preventing intelligence degradation.
- **Anti-Slop Weight Engineering:** Permanently suppresses AI clichés (*tapestry, ethereal, celestial, beacon, kaleidoscopic*) at the probability weight level via `config.noslop.toml`.
- Technical details documented in: [`~/.gemini/knowledge/heretic_llm_abliteration_and_steering.md`](file:///~/.gemini/knowledge/heretic_llm_abliteration_and_steering.md).
