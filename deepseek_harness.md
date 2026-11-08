# DeepSeek Terminal Harness & OMP Protocol

## Invariants

1. **Hash-Anchored Precision Edits (`hashline` Protocol):** Inspect exact syntactic anchors (50-100 lines) immediately before editing. Replace only modified lines.
2. **In-Process LSP & Diagnostic Loop:** Run compiler/linter diagnostics after every edit. Fix errors within 3 bounded iterations.
3. **Git Worktree Isolation:** High-risk refactoring executes in isolated git worktrees (`.worktrees/task-<id>`).
4. **Decoupled Dual-Model Steering:**
   - **Worker:** Fast, bounded execution of edits, queries, and tests.
   - **Advisor:** Adversarial reflection assessing invariant preservation, edge cases, and confidence score.