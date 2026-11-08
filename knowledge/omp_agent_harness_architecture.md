# OMP (Oh-My-Pi) Agent Harness Architecture & Deterministic Execution Protocol

> **Reference Repository:** [can1357/oh-my-pi](https://github.com/can1357/oh-my-pi) (`omp`) by Can Bölük (`can1357` / Stencil Labs)  
> **Ecosystem Evolution:** Forked and expanded from Mario Zechner's minimalist `pi` agent into a batteries-included terminal coding harness.  
> **Core Objective:** Transforming fast LLMs (such as Gemini 3.8 Flash) from unstable, amnesia-prone conversational models into disciplined, deterministic software engineering agents.

---

## 1. The Foundational Problem: The LLM Engine vs. The Agent Harness

In autonomous software engineering, the LLM is merely the **reasoning engine**, while the **harness** is the vehicle, chassis, and sensory-motor feedback loop:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        UNHARNESSED LLM (VULNERABLE)                    │
│                                                                        │
│  User Request ──► [ Raw LLM ] ──► Guesses Line Numbers & Signatures   │
│                          │         └── Dumps Full 1,000-line Files     │
│                          ▼         └── Suffers Attentional Decay       │
│                  Brain Fog / Amnesia                                   │
└────────────────────────────────────────────────────────────────────────┘

                                    VS

┌────────────────────────────────────────────────────────────────────────┐
│                    OMP DETERMINISTIC HARNESS (ROBUST)                  │
│                                                                        │
│  User Request ──► [ OMP Tool Harness ] ──► Worktree Task Isolation     │
│                          │              ──► Hashline Anchored Edits    │
│                          │              ──► In-Process LSP Diagnostics │
│                          ▼              ──► Decoupled Advisor Audit    │
│                  [ Grounded Engine ]    ──► Bounded Context Compaction │
│                          ▲                                             │
│                          └─────── Closed Feedback Loop ────────────────┘
└────────────────────────────────────────────────────────────────────────┘
```

### Why Unharnessed Fast Models Suffer from "Context Amnesia" & Failure Loops:
1. **Line Number Drift & Diff Hallucination:** Standard line-number patching breaks the moment indentation changes or previous edits shift offsets. The LLM guesses lines, misses indentation, and corrupts source files.
2. **Context Window Inflation & Token Burn:** Full-file rewrites dump thousands of tokens per turn. At turn 15, the model's context is 95% redundant code dumps and terminal noise, triggering the **Lost-in-the-Middle** phenomenon where the model forgets early architectural constraints.
3. **Open-Loop Mutation (No Diagnostics):** Emitting code without inspecting compiler diagnostics or syntax trees leads to blind trial-and-error patching.
4. **Subtask Contamination:** Running multi-file refactoring on the working tree pollutes Git status, making safe rollback or parallel worker execution impossible.

---

## 2. Pillar 1: Hash-Anchored Precision Edits (`hashline`)

The signature innovation of `oh-my-pi` is **Hashline Edits** (`hashline`):

### 2.1. Mechanism & Mathematical Anchor
Instead of relying on volatile absolute line numbers (`L145-L160`) or fragile multi-line fuzzy matching, OMP calculates a cryptographic or short hash (e.g. 2–4 byte FNV-1a / CRC / xxHash) for lines or blocks:
- Each target line or boundary is indexed by `[content_hash]`.
- The mutation instruction specifies:
  ```text
  TARGET_ANCHOR: #h:<hash_before> ... <content> ... #h:<hash_after>
  REPLACEMENT:   <new_lines>
  ```
- If the file has shifted due to earlier edits, the anchor hash remains invariant to vertical line offset shifts.
- If the content inside the anchor changed unexpectedly, the hash validation fails immediately before corrupting the file, forcing an immediate re-read instead of a silent corruption.

### 2.2. Token & Performance Benefits
- **61% Token Reduction:** Bounded replacements require emitting only the modified lines and 1–2 anchor hashes, rather than 500+ lines of surrounding boilerplate.
- **Zero Whitespace Ambiguity:** Resolves Python indentation drift and tab-versus-space mismatch errors.

---

## 3. Pillar 2: In-Process Language Server & Compiler Diagnostic Harness (LSP & DAP)

OMP embeds developer tooling directly into the execution loop rather than relying exclusively on raw bash commands:

### 3.1. Language Server Protocol (LSP) Closed Loop
Before and after code modifications, OMP queries the language server (`Pyright`, `gopls`, `tsserver`, `rust-analyzer`, `clangd`):
1. **Pre-Flight Symbol Grounding:** Inspects exact symbol definitions, parameter types, caller hierarchies, and implementors before modifying interfaces.
2. **Post-Flight Diagnostic Gate:** Immediately after a patch is applied, the harness inspects LSP diagnostics:
   - Errors (`severity: 1`)
   - Warnings (`severity: 2`)
   - Unused imports / unreachable code (`severity: 3`)
3. **Deterministic Auto-Remediation:** If an edit introduces a diagnostic regression, the harness halts delivery, reports the diagnostic trace to the LLM, and triggers targeted remediation before notifying the user.

### 3.2. Debug Adapter Protocol (DAP)
Connects directly to native debuggers (`debugpy`, `dlv`, `lldb-dap`):
- Sets dynamic breakpoints at suspect functions.
- Inspects stack frames, local variables, and heap references during test execution.
- Separates symptom from root cause through deterministic backward execution tracing.

---

## 4. Pillar 3: Sub-Agent Task Isolation via Git Worktrees (`task` Harness)

Complex, high-risk, or parallel tasks must never execute directly in the main working tree:

### 4.1. Worktree Isolation Protocol
1. **Branch & Worktree Creation:**
   ```bash
   git worktree add ../.worktrees/task-<task_id> -b task/<task_id>
   ```
2. **Sub-Agent Sandboxing:** The sub-agent operates strictly within `task-<task_id>`. It has full read/write access to test, compile, and run benchmarks without risking the user's uncommitted work.
3. **Structured Schema Delivery:** When complete, the sub-agent returns a structured JSON payload:
   ```json
   {
     "task_id": "refactor-auth-tokens",
     "status": "VERIFIED",
     "files_modified": ["auth/token.go", "auth/token_test.go"],
     "tests_passed": 14,
     "tests_failed": 0,
     "git_commit": "e3a891f",
     "diagnostics_clean": true
   }
   ```
4. **Parent Cherry-Pick / Merge:** The parent agent reviews the verified diff and merges or cherry-picks the commit into the primary branch. If the subtask fails, the worktree is cleanly pruned (`git worktree remove --force`) with zero blast radius on the primary workspace.

---

## 5. Pillar 4: Decoupled Multi-Model Steering & In-Loop Advisor (`/advisor`)

OMP avoids using a single LLM configuration for every operation. It decouples execution from verification:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        OMP DUAL-MODEL LANES                            │
├────────────────────────────────┬───────────────────────────────────────┤
│ Worker Role (Fast Executor)    │ Advisor Role (Adversarial Verifier)   │
├────────────────────────────────┼───────────────────────────────────────┤
│ • Gemini 3.8 Flash / Qwen 27B  │ • Gemini 3.8 High / Claude 3.7 Sonnet │
│ • High-speed tool execution    │ • Blind to Worker's rationalizations  │
│ • File reading, editing, diffs │ • Invariant protection audit          │
│ • Unit test execution          │ • Blast radius & regression checker   │
│ • Line-level syntax operations │ • Final Kage confidence scoring (≥98%)│
└────────────────────────────────┴───────────────────────────────────────┘
```

### The Advisor Verification Protocol:
1. When a task modifies core business logic, schema migrations, or >2 files, the **Advisor role** is invoked before final delivery.
2. The Advisor is instructed with an adversarial posture: *"Audit this proposed change for regressions, unhandled edge cases, hidden N+1 queries, race conditions, and ungrounded assumptions."*
3. If the Advisor identifies an invariant violation, it halts execution with concrete evidence, forcing the Worker to resolve the defect.

---

## 6. Pillar 5: Dynamic Context Compaction & Anti-Amnesia Token Hygiene

To prevent Gemini 3.8 Flash from losing attention during long multi-turn sessions:

### 6.1. Tactical Context Compaction
1. **Terminal Noise Stripping:**
   - Strip build progress bars (`[===>   ] 42%`), repetitive download logs, and verbose package manager outputs.
   - Retain only: Exit Code, Invoked Command, and First/Last 15 lines of error logs.
2. **Bounded File Range Reads:**
   - Strictly prohibit unindexed full-file dumps. Inspect files in targeted 50–100 line ranges (`StartLine` and `EndLine`).
3. **State Ledger Maintenance (`[PROGRESS STATE]`):**
   - Continuously update an atomic ledger in scratchpad memory:
     - `Completed:` Tasks verified with clean tests.
     - `Active:` Current file, line range, and active hypothesis.
     - `Remaining:` Pending verification gates.
4. **Periodic Re-Anchoring:**
   - Re-inject core invariants (user identity User, hardware constraints, zero-vibe coding rule) across conversation milestones.

---

## 7. Operational Checklist for OMP Harness Conformance

Before marking any coding task complete under the OMP Harness:
- [ ] **Hash / Anchor Grounding:** Did the edit target exact verified lines without guessing?
- [ ] **LSP / Diagnostic Verification:** Are all compiler and linter diagnostics clean (exit code 0, zero type errors)?
- [ ] **Regression Audit:** Were existing unit tests executed to verify zero downstream blast radius?
- [ ] **Advisor Self-Review:** Did an adversarial check pass with ≥ 98% confidence?
- [ ] **Zero Redundant Context:** Was terminal output bounded and free of token bloat?
