# AGENTS.md - Universal AI Coding Agent Specification

> **Specification Standard:** [Agentic AI Foundation (AAIF) / Linux Foundation](https://agents.md/)  
> **Supported Harnesses:** Antigravity, Cursor, Claude Code, OpenAI Codex, Devin, Windsurf, Aider, Goose

---

## 1. Agent Architecture & Precedence

1. **Chat Prompt:** Direct prompt instructions take highest authority.
2. **Nested AGENTS.md:** Closest nested directory specification overrides root rules.
3. **Root AGENTS.md:** This repository instruction manifest.
4. **Modular Skills:** Load domain instructions from `skills/<name>/SKILL.md` on demand.

---

## 2. Mandatory Engineering Invariants

- **Deterministic Engineering over Vibe Coding:** Never guess signatures or apply speculative patches.
- **Evidence Over Assumptions:** Categorize reasoning as Verified, Inferred, Assumed, or Unknown.
- **5 Quality Gates:** Enforce Gate 1 (Blast Radius) through Gate 5 (Reflexion) on all non-trivial PRs.
- **Bounded File Inspection:** Bound reads to 50–100 lines at a time.
- **Zero AI Slop:** Suppress conversational sycophancy, AI jargon, and syntax-narrating comments.

---

## 3. Skill & Tool Router

Refer to `core/ROUTER.md` for the progressive disclosure matrix.