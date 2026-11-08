# AGENTS.md Universal Open Standard Specification

> **Official Repository:** [agentsmd/agents.md](https://github.com/agentsmd/agents.md)  
> **Official Website:** [https://agents.md/](https://agents.md/)  
> **Stewardship:** Agentic AI Foundation (AAIF) under the Linux Foundation  
> **Founding Collaborators:** OpenAI (Codex), Google (Jules & Gemini CLI), Cursor, Amp, Factory, Cognition (Devin & Windsurf), Aider, Goose (Block), GitHub Copilot, Zed, Warp, RooCode, OpenCode.

---

## 1. Philosophy & Background: "A README for AI Agents"

Prior to `AGENTS.md`, the AI coding ecosystem was fragmented across competing proprietary configuration files (`.cursorrules`, `.windsurfrules`, `CLAUDE.md`, `.copilot-instructions.md`, `.aider.conf.yml`).

`AGENTS.md` establishes a **universal, vendor-neutral open standard**:
- **`README.md` is for humans:** High-level project overviews, quickstarts, architectural vision, and contribution onboarding.
- **`AGENTS.md` is for AI coding agents:** Deterministic technical instructions, exact build/test commands, dev server HMR invariants, import conventions, and linting parameters that would otherwise clutter human-facing documentation.

---

## 2. Resolution Hierarchy & Scoping Precedence

When an agent operates within a codebase, instruction precedence follows:

```
[Explicit User Prompt in Chat] (Highest Authority - Always Overrides)
               │
               ▼
   [Closest Nested AGENTS.md] (Subproject / Monorepo Package Level)
               │
               ▼
      [Root AGENTS.md] (Repository Root)
               │
               ▼
[Global Agent Rules / ~/.agents/AGENTS.md / Gemi Knowledge]
```

1. **Explicit Prompt Override:** Direct instructions from User in chat take immediate precedence over static `AGENTS.md` directives.
2. **Nearest File Wins (Monorepo Scoping):**
   - In large monorepos, individual packages can ship localized `AGENTS.md` files (e.g., the primary OpenAI repository contains 88 `AGENTS.md` files).
   - The agent **must prioritize the `AGENTS.md` closest in the directory hierarchy** to the file being edited.
3. **Living Documentation:** `AGENTS.md` is treated as living documentation, updated iteratively alongside CI workflows and dependency migrations.

---

## 3. Standard File Structure

While standard Markdown without rigid schemas is used, the following canonical sections are recognized:

### 3.1. Dev Environment Tips
- Efficient monorepo navigation without token-wasting `ls` scans (e.g., `pnpm dlx turbo run where <package>`).
- Canonical package manager (`pnpm`, `uv`, `cargo`, `go`, `composer`).
- Scoped dependency installation (e.g., `pnpm install --filter <package_name>`).

### 3.2. Dev Server vs Production Build Conventions
- **Hot Module Replacement (HMR) Rule:** Always run the development server (`npm run dev` / `pnpm dev`) during interactive agent workflows.
- **Interactive Build Prohibition:** Never run `npm run build` during interactive coding sessions if it overwrites `.next`/`.dist` with production assets, breaks hot reload, or leaves the dev server in an inconsistent state.

### 3.3. Testing Instructions (Automated Check Contract)
- Location of CI configurations (e.g., `.github/workflows`).
- Granular test commands (e.g., `pnpm vitest run -t "<test_name>"`).
- **Agent Contract:** When test/lint commands are listed, the agent is expected to execute relevant programmatic checks automatically and remediate failures until all suites are green before concluding work.
- Proactive standard: *"Add or update tests for the code you change, even if nobody asked."*

### 3.4. Code Style & Architecture Guidelines
- Language and extension conventions (e.g., TypeScript `.tsx`/`.ts` required for all new modules).
- Co-location: Placing unit tests and styles adjacent to their corresponding components.
- Anti-patterns: Banning `any` types, circular imports, and monolithic file bloating.

### 3.5. PR & Commit Instructions
- Structured commit/PR title formats (e.g., `[<package_name>] <Title>`).
- Pre-commit hygiene checks (`pnpm lint`, `pnpm test`).

---

## 4. Cross-Agent Compatibility Matrix

`AGENTS.md` is natively supported across major agent surfaces:
- **Google / DeepMind:** Jules, Gemini CLI (`settings.json -> context.fileName: "AGENTS.md"`), Antigravity IDE.
- **OpenAI:** Codex CLI, Operator.
- **Anthropic / Claude Code:** Automated reading of `AGENTS.md` / `CLAUDE.md`.
- **Cursor & Windsurf:** Native workspace context discovery.
- **Terminal CLI Harnesses:** Aider (`.aider.conf.yml -> read: AGENTS.md`), OMP (Oh-My-Pi), Goose (Block), OpenCode, RooCode, Zed, Warp.

---

## 5. Gemi Operating Invariants for `AGENTS.md`

1. **Auto-Discovery:** Prior to editing code in any workspace, Gemi inspects the root and active module folders for `AGENTS.md`.
2. **Strict Adherence:** Any test commands, lint checks, or build prohibitions defined in `AGENTS.md` must be followed deterministically.
3. **Zero Contamination:** Never mix internal agent instructions into human-facing `README.md` files when `AGENTS.md` is present.
