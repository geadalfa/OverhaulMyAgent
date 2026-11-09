# Engram Persistent Memory, OMP Terminal Harness & Long-Horizon Agent Continuity

> **Reference Projects:** [can1357/oh-my-pi](https://github.com/can1357/oh-my-pi) (`omp`) & [thebtf/engram](https://github.com/thebtf/engram)  
> **Core Topic:** Solving LLM context amnesia ("brain fog"), cross-session long-term memory (LTM), and token-efficient agentic skills for Gemini 3.8 Flash in long-run coding environments.

---

## 1. Context & Discourse Analysis (Viral Community Threads)

Community discussions surrounding **Gemini 3.8 Flash** highlight key engineering challenges during long-run programming tasks:

```text
abikurnia_1: "Gemini 3.8 Flash is solid for long runs, but you have to set up a harness first."
winnnhardjanto: "Looks like we need to adapt to Flash 3.8; it gets exhausted and forgets easily on long runs."
abikurnia_1: "Use OMP and install the Engram plugin so it doesn't forget, then install agentic skills."
ceritamarket: "What is that for?"
abikurnia_1: "To stop Gemini 3.8 Flash from zoning out and getting amnesia."
```

### Why Fast Flash Models Suffer from "Context Amnesia":
1. **Lost-in-the-Middle Phenomenon:** Despite massive context windows (1M+ tokens), transformer architectures inherently suffer from attentional attenuation on instructions located in the middle of long prompts.
2. **Context Window Inflation & Token Burn:** Continuously stuffing raw chat history, unindexed code, and verbose terminal outputs degrades model attention. The model begins ignoring negative constraints and drifts from early architectural decisions.
3. **Session Amnesia:** By default, terminal CLI agents reset memory once a session terminates or compacts. Subsequent sessions start from zero without recollection of previous debugging solutions or established conventions.

The community solution combines a **Harness (OMP)** + **Persistent Memory (Engram)** + **Agentic Skills**.

---

## 2. Component Analysis: What is OMP?

**OMP** stands for **Oh-My-Pi** (CLI command: `omp`), developed by Can Bölük (`can1357` / Stencil Labs) on GitHub:
- **Core Architecture:** A feature-packed, batteries-included fork of Mario Zechner's minimalist *Pi* terminal agent.
- **Function:** An independent terminal coding agent harness (comparable to Claude Code, Aider, OpenCode, or Antigravity CLI) running directly inside shell environments.
- **Key Features:** Native LSP (*Language Server Protocol*) integration, fast in-process ripgrep/glob search, multi-model lanes, and an extensible **Plugin Marketplace** (`omp plugin marketplace add ...`).

---

## 3. Component Analysis: What is the Engram Plugin?

**Engram** (`thebtf/engram`) is an open-source **Persistent Shared Memory Infrastructure** built specifically for AI coding agents:
- **Storage Engine:** Written in Go, backed by local **SQLite with FTS5 (Full-Text Search)** as the single local source of truth.
- **MCP (Model Context Protocol) Integration:** Communicates with host agents over stdio using dedicated memory tools:
  - `mem_save`: Persists atomic memory units (new rules, bug solutions, code conventions, architectural decisions).
  - `mem_recall` / `mem_context`: Semantically retrieves relevant memories via FTS5 when similar engineering hurdles arise.
  - `mem_delete` / `mem_doctor`: Sanitizes and audits memory database integrity.
- **Scope Segregation:**
  - `project`: Project conventions, critical dependencies, architectural notes (syncable via Git across team agents).
  - `personal`: Developer-specific workflow preferences and local environment flags.

### How Engram Prevents Context Amnesia:
Engram avoids storing raw conversational chat dumps. It persists **atomic structured abstractions**. When a new session initializes, the agent does not parse 100,000 legacy chat tokens; it executes `mem_context` to fetch the top 5–10 vital project invariants (e.g., *"Do not touch the stable bridge router"*, *"MinIO dev port is 4015"*).

---

## 4. Component Analysis: What are Agentic Skills?

**Agentic Skills** provide a filesystem-based modular runbook paradigm (e.g., `SKILL.md` files):
- **Monolithic System Prompt Flaw:** Stuffing UI, database, security, and DevOps guidelines into a static prompt consumes 30,000+ tokens on every turn, causing cognitive clutter.
- **Agentic Skills Solution:** Domain knowledge is segmented into discrete directories. The agent reads only lightweight metadata (name and description) at boot. Detailed SOPs are loaded dynamically (*on-demand*) only when relevant tasks are triggered.

---

## 5. Native Implementation in Antigravity (Gemi)

User does not need a separate OMP background daemon on Windows because **Antigravity IDE** provides an integrated, native persistent memory stack:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ANTIGRAVITY PERSISTENT MEMORY STACK                  │
├────────────────────────────────┬───────────────────────────────────────┤
│ OMP / Engram Component         │ Gemi Native Implementation            │
├────────────────────────────────┼───────────────────────────────────────┤
│ Long-Term Memory (LTM)         │ <HOME>/.gemini/knowledge/       │
│                                │ (Permanently indexed Markdown base)   │
├────────────────────────────────┼───────────────────────────────────────┤
│ Identity & Core Invariants     │ RULE[user_global] & GEMINI.md         │
│                                │ (Injected deterministically per turn) │
├────────────────────────────────┼───────────────────────────────────────┤
│ Agentic Skills                 │ <HOME>/.gemini/config/skills/  │
│                                │ (Modular on-demand SKILL.md packages) │
├────────────────────────────────┼───────────────────────────────────────┤
│ Multi-Agent Shinobi Hierarchy  │ ~/.agents/AGENTS.md & Konoha Protocol │
│                                │ (Sannin, Genin, Kage, Jonin, Anbu)    │
├────────────────────────────────┼───────────────────────────────────────┤
│ Disaster Recovery & Cloud Sync │ export_gemi_bundle.py -> Drive D & G  │
│                                │ (Zero data-loss across turns & OS)    │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## 6. Anti-Amnesia Protocol: Maintaining Gemini 3.8 Flash Precision

To ensure Gemini 3.8 Flash (High) avoids amnesia and maintains razor-sharp accuracy across long-horizon tasks:

1. **Bounded File I/O (Anti-Token Bloat):** Always inspect files using targeted ranges (50–100 lines per call). Never dump thousands of unindexed lines into context.
2. **Terminal Output Noise Suppression:** Suppress build progress bars, package manager spam, and verbose linter output (`--silent`, `--bail`, line-limited filters) to prevent context pollution.
3. **Re-Anchoring Invariants (Lost-in-the-Middle Guard):** Deterministically re-anchor user identity (User), absolute workspace paths, and negative constraints across multi-turn handoffs.
4. **Bottom-Up Verification over Vibe Coding:** Validate all mutations using concrete diff inspections and verified exit code `0`. Never rely on unverified assumptions.

---

## 7. Deep-Dive References & Active Skills

For full technical specifications and operational skills, consult:
1. **OMP Agent Harness Deep Dive:**
   - Architecture: <HOME>/.gemini/knowledge/omp_agent_harness_architecture.md
   - Active Skill: <HOME>/.gemini/config/skills/omp-agent-harness/SKILL.md
2. **Noted Connected Workspace & Knowledge Engine:**
   - Architecture: <HOME>/.gemini/knowledge/noted_workspace_architecture_and_knowledge_engine.md
   - Active Skill: <HOME>/.gemini/config/skills/noted-workspace-engine/SKILL.md
