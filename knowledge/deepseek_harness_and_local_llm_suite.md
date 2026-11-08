# DeepSeek Harness & Local LLM Suite Architecture & Operational Registry

This document records the exact configuration, filesystem paths, runtime daemons, model architectures, troubleshooting history, and automation scripts established for the **DeepSeek Harness + Local LLM Suite** on User\'s Windows workstation.

---

## 1. Local Filesystem Paths & Service Registry

| Component | Exact Filesystem Path | Protocol / Port | Role & Configuration |
| :--- | :--- | :--- | :--- |
| **DeepSeek Harness GUI** | I:\Program Files (x86)\Deepseek Harness\DeepSeek Harness.exe | Electron Desktop GUI | Primary AI agent chat & interface. |
| **DeepSeek Harness Profile** | ~\.dsh\profiles\desktop\cordis.patch.yml | YAML Configuration | Configures TabbyAPI & Ollama providers, ultra-lightweight prompt, web search MCP. |
| **Steering Invariants** | ~\.dsh\AGENTS.md & workspace AGENTS.md | Markdown (< 1 KB) | Clean Gemi persona and zero-nausea gaming ergonomics without token bloat. |
| **TabbyAPI Inference Server** | <LOCAL_LLM_DIR>
| **TabbyAPI Configuration** | <LOCAL_LLM_DIR>
| **Primary EXL2 Model** | <LOCAL_LLM_DIR>
| **Ollama Daemon & Models** | <LOCAL_LLM_DIR>
| **Lifecycle Orchestrator** | <LOCAL_LLM_DIR>
| **Silent VBS Runner** | <LOCAL_LLM_DIR>
| **Desktop Shortcut** | ~\Desktop\DeepSeek Harness.lnk | Windows Shortcut | Directly triggers launch_deepseek_harness.vbs. |
| **GitHub Export Repository** | <LOCAL_LLM_DIR>

---

## 2. Active Model Hierarchy

1. **TabbyAPI - Qwen2.5-Coder-7B-Instruct-exl2-4_25 (Default Daily Driver):**
   - **Context Window:** **131,072 tokens (128K)**.
   - **Cache Mode:** **Q8** (8-bit quantized KV-cache).
   - **Inference Speed:** **120 – 140 Tokens/Sec** on Dedicated GPU (12 GB+ VRAM).
   - **VRAM Allocation:** ~8.0 GB / 12 GB, leaving ample headroom for OS & display compositor.

2. **TabbyAPI - Qwen2.5-7B-Instruct-1M-exl2-4_25:**
   - **Context Window:** **131,072 tokens (128K)**.
   - **Cache Mode:** **Q8** (~7.8 GB total VRAM).
   - **Specialization:** General instruction, long multi-turn chats, polyglot fluency.

3. **TabbyAPI - Mistral-Nemo-Instruct-2407-exl2-4_25:**
   - **Context Window:** **131,072 tokens (128K)**.
   - **Cache Mode:** **Q4** (~9.5 GB total VRAM).
   - **Specialization:** High precision instruction following, balanced reasoning.

4. **TabbyAPI - Qwen2.5-14B-Instruct-1M-exl2-4_25:**
   - **Context Window:** **65,536 tokens (64K)**.
   - **Cache Mode:** **Q4** (~11.2 GB total VRAM).
   - **Specialization:** Deep complex reasoning and system architecture.

5. **Ollama - deepseek-r1:7b:**
   - **Context Window:** **131,072 tokens (128K)**.
   - **Specialization:** Chain-of-Thought (CoT) pure reasoning, mathematics, logic.

6. **Ollama - qwen2.5-coder:7b:**
   - **Context Window:** **131,072 tokens (128K)**.
   - **Specialization:** Polyglot code generation.

7. **Ollama - qwen3.8:27b-ista-das:**
   - **Context Window:** **65,536 tokens (64K)**.
   - **Specialization:** 27B parameter deep analysis, high-complexity problem solving.

---

## 3. Native Default Preset & Tool Integration

To preserve full agent capabilities and system environmental awareness:
- **Default Agent Preset:** DeepSeek Harness standard preset is restored to default, preserving @deepseek-ai/dsh-time-context (current date & machine clock), 	ool-pwsh (PowerShell command execution), 	ool-fs (filesystem inspection), planning, compaction, and subagent tools.
- **Root Cause of Previous Anomaly:** Overriding preset-standard with includeRuntimeContext: false and stripping dsh-time-context caused the model to lose awareness of the current machine time/date and prevented shell execution, leading to 'tidak dapat menentukan waktu' refusals.
- **Web Search Integration:** Retains duckduckgo-search MCP client (
px -y duckduckgo-mcp) alongside built-in 	ool-web for zero-API-key internet search.

---

## 4. Zero-Overhead Lifecycle & Gaming Invariant

User is an active PC gamer. Having heavy background AI processes idling consumes valuable RAM and VRAM, causing game stutter and FPS drops.
- **Windows Startup:** Ollama is explicitly removed from HKCU:\Software\Microsoft\Windows\CurrentVersion\Run. Startup impact is **0 MB RAM & 0 MB VRAM**.
- **On-Demand Spin-Up:** Double-clicking DeepSeek Harness.lnk triggers launch_deepseek_harness.vbs, which boots ollama serve and TabbyAPI (main.py) silently.
- **Instant Kill on Exit:** When User closes the DeepSeek Harness window, the monitoring loop immediately terminates Ollama and TabbyAPI to return 100% of RAM and VRAM to Windows.
