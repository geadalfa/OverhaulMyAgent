---
name: omp-agent-harness
description: Apply the Oh-My-Pi (OMP) terminal agent harness protocol to enforce deterministic hash-anchored edits, in-process LSP/DAP diagnostic verification, git worktree task isolation, dual-model Advisor verification, and anti-amnesia context compaction.
---

# OMP Agent Harness Operating Skill

This skill operationalizes the architecture of **Oh-My-Pi** (`can1357/oh-my-pi` - `omp`), turning fast LLM engines (like Gemini 3.8 Flash) into deterministic, self-verifying engineering agents that resist context decay, line-number drift, and hallucinated diffs.

---

## 1. When to Activate This Skill

Activate this skill whenever:
- Executing code refactoring, bug fixes, or feature additions across 1 or more files.
- Modifying mission-critical business logic, state machines, or database queries.
- Working in long multi-turn sessions where the agent risks token fatigue or context amnesia.
- Spawning sub-agents to parallelize tasks or execute high-risk experimental patches.

---

## 2. Core Protocol 1: Deterministic Hash-Anchored Editing (`hashline`)

Standard line-number patching (`edit_file` with fuzzy lines) easily drifts when preceding lines change. The OMP harness enforces:

### 2.1. Grounding Target Anchors
1. **Never guess surrounding lines:** Inspect the exact target region using bounded reads (50–100 lines) immediately before issuing an edit.
2. **Anchor Identification:** Pick unique syntactic anchors (e.g. function signature, unique variable declaration, or closing bracket) that cannot match duplicate blocks elsewhere in the file.
3. **Smallest Atom of Mutation:** Do NOT rewrite entire files. Replace only the minimal continuous lines required to implement the verified change.
4. **Post-Mutation Readback Verification:** After applying the edit, immediately read back the modified line range to confirm indentation, syntax validity, and surrounding context integrity.

---

## 3. Pillar 2: In-Process Compiler & Diagnostic Feedback Loop (LSP/DAP Gate)

Never consider a mutation complete upon mere file-save. The harness mandates a closed diagnostic loop:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DIAGNOSTIC FEEDBACK LOOP                        │
│                                                                        │
│   Apply Mutation ──► Run Typecheck / Linter / Test ──► Exit Code 0?   │
│                             │                                  │       │
│                             │                                  ├── YES ──► Commit & Proceed
│                             ▼                                  │       │
│                      Diagnostic Errors                         └── NO  ──► Targeted Auto-Fix
│                             │                                          │   (Loop <= 3 retries)
│                             └────────── Feedback to Agent ─────────────┘
└────────────────────────────────────────────────────────────────────────┘
```

### 3.1. Diagnostic Commands by Ecosystem
- **Go (`backend-pr-review-repositories`):**
  ```bash
  go vet ./... && golangci-lint run --fast
  ```
- **TypeScript / React / Node.js:**
  ```bash
  npx tsc --noEmit && npm run lint --silent
  ```
- **Python (`DiagnoseMyDisk`, `db_query`, etc.):**
  ```powershell
  python -m py_compile <modified_file>.py
  flake8 <modified_file>.py --select=E9,F63,F7,F82 --show-source
  ```

---

## 4. Pillar 3: Sub-Agent Task Isolation via Git Worktrees (`task` Delegation)

When an operation requires exploratory debugging, complex multi-file refactoring, or running long benchmark suites, do NOT contaminate the primary branch:

1. **Spawn Worktree Sandbox:**
   ```bash
   git worktree add ../.worktrees/task-<name> -b task/<name>
   ```
2. **Delegate Sub-Agent:**
   - Sub-agent operates exclusively inside `../.worktrees/task-<name>`.
   - Sub-agent runs tests, modifies files, and records results.
3. **Deliver Schema-Validated Return:**
   - The sub-agent must return a structured JSON report (modified files, passing tests, commit SHA).
4. **Integrate or Prune:**
   - On success: Parent merges or cherry-picks the commit.
   - On failure: Prune cleanly with `git worktree remove --force ../.worktrees/task-<name>` and `git branch -D task/<name>`.

---

## 5. Pillar 4: Decoupled Multi-Model Steering & In-Loop Advisor (`/advisor`)

To protect against self-rationalizing errors:
1. **Worker Role:** Fast execution of file reads, edits, and standard unit tests.
2. **Advisor Role (Adversarial Reflexion):**
   - Triggered before concluding any major task.
   - Evaluates:
     - *Are there unhandled nil pointers or edge conditions?*
     - *Does this query cause an N+1 performance bottleneck?*
     - *Is there any accidental deletion of docstrings or comments?*
     - *Does the change meet the Kage 98% confidence threshold?*

---

## 6. Pillar 5: Anti-Amnesia Token Hygiene & Bounded Context

To keep Gemini 3.8 Flash operating with maximum focus:
1. **Suppress Terminal Noise:** Filter build outputs. Never allow hundreds of lines of compiler logs into context.
2. **Strict Range Bounding:** Prohibit reading > 100 lines at once unless strictly necessary.
3. **Atomic State Ledger:** Maintain `[PROGRESS STATE]` tracking at every conversational milestone.
4. **Immediate Negative Constraint Re-Anchoring:** Verify that critical invariants (User's gaming ergonomics, zero-slop rules, database isolation) are preserved across all generated code.
