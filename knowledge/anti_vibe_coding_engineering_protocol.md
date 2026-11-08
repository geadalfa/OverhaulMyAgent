# Ultimate Engineering, Architecture, & Anti-Vibe-Coding Protocol

## 1. Executive Directive: Deterministic Engineering Over Vibe Coding
This protocol enforces **Deterministic, Evidence-Based Engineering**. Because language models tend to guess missing context and jump prematurely into code generation ("vibe coding"), the agent MUST strictly enforce **Externalized Reasoning**: no implementation code or bug patches may be applied until verification, blast radius, distributed resilience, failure modes, and execution steps are explicitly articulated.

---

## 2. Zero-Hallucination & Codebase Grounding Rules
1. **Never Invent APIs, Methods, or Signatures:**
   - Guessing internal functions, class signatures, ORM syntax, or library endpoints is strictly forbidden.
   - Inspect the actual file, interface, or dependency manifest (`package.json`, `go.mod`, `pom.xml`, etc.) before referencing any symbol.
2. **Respect Existing Codebase Architecture:**
   - Inspect 1–2 existing modules to mirror directory structure, naming conventions, DTO validation patterns, logging format, and error handling.
   - Never introduce unvetted patterns or external libraries when established patterns exist in the repository.
3. **Use Tools & Codebase Search First:**
   - Always query tools (symbol search, grep, view_file, MCP) to ground facts before formulating answers.
4. **No Premature Implementation:**
   - If a task touches >2 files, changes business workflows, or alters database schemas, do not write implementation code in the first turn. Pass Quality Gates 1 through 3 first.
5. **Stop and Clarify Ambiguities:**
   - Stop immediately when state transitions, business rules, or security boundaries are ambiguous. Present 2–3 concrete options with explicit trade-offs.
6. **Ground in Repository AGENTS.md (Universal Agent Standard):**
   - Always inspect the root or closest nested `AGENTS.md` (Linux Foundation / AAIF standard) before touching code.
   - Extract specific dev server conventions, test execution flags, and architectural invariants defined by the repo owners.
7. **Mandatory English for Knowledge, Skills, Rules & Steering:**
   - All newly authored or updated knowledge base files (`~/.gemini/knowledge/`), agent skills (`~/.gemini/config/skills/`), rule templates, and architectural specs MUST strictly be written in concise English to maximize BPE token efficiency (~30%–50% token reduction) and prevent context degradation.
8. **Mandatory Pre-Flight Capability & Inventory Audit (Rules, Configs, Tools, MCP, Skills First):**
   - Before executing any instruction or writing code, audit operational rules, configs, local tool scripts (`~/.gemini/scripts/`), active MCP servers, registered skills (`~/.gemini/config/skills/`), and persistent memory.
   - Never write ad-hoc throwaway scripts or trial-and-error implementations when specialized tools or workflows already exist.

---

## 3. The 5 Quality Gates

### Gate 1: Requirement Parsing & Blast Radius Discovery
- **Flow Deconstruction:** `Trigger/Actor -> Input Validation -> State Machine / Business Rules -> Data Persistence -> Side Effects / Async Events`.
- **Blast Radius Mapping:** Explicitly list direct (files, tables, endpoints), indirect (callers, consumers, shared libraries, reports), and operational impacts (deploy order, migrations, rollback).
- **Backward Compatibility:** Ensure additive changes that preserve live client and inter-service compatibility.
- **Mandatory Failure Scenarios:** Define at least 3 concrete failure cases (e.g. malformed inputs, duplicate concurrent requests, downstream timeouts, partial writes) and their recovery behavior.

### Gate 2: Microservice Boundaries & Distributed Systems Resilience (DDIA & DDD)
- **Visual Sequence Mapping:** Use sequence diagrams or flowcharts (`mermaid`) to illustrate both **Happy Paths** and **Compensation/Rollback Paths**.
- **Contract-First Design:** Formulate explicit request/response schemas or event payloads before writing handlers.
- **Strict Database Isolation:** Never query or `JOIN` another microservice's database tables directly. Use versioned APIs or asynchronous messaging.
- **Idempotency by Default:** All mutating operations (`POST`, `PUT`, `PATCH`, queue consumers) must be idempotent using unique idempotency keys, unique database constraints, or state guard clauses (`WHERE status = 'PENDING'`).
- **Anti-Dual-Write Protection:** Avoid updating a database and calling an external service or message broker naively. Use the **Transactional Outbox Pattern**, idempotent retry workers, or explicit **Saga Compensation** logic.
- **Network Fault Tolerance:** Enforce explicit connection/read timeouts, exponential backoff with jitter, circuit breakers, and Dead-Letter Queues (DLQ). Never use empty `catch {}` blocks.

### Gate 3: Database Architecture, Performance & Concurrency
- **Index Verification:** Verify indexing on `WHERE`, `JOIN`, and `ORDER BY` columns, respecting composite left-prefix order and cardinality.
- **Zero N+1 Queries:** Strictly prohibit queries or remote network calls inside loops (`for`, `map`, `forEach`). Enforce batch operations (`WHERE id IN (...)`) or bulk inserts.
- **Short Transaction Boundaries:**
  - Wrap multi-table modifications in atomic transactions (`BEGIN` / `COMMIT` / `ROLLBACK`).
  - **CRITICAL:** Never place external HTTP/gRPC calls, file uploads, hashing, or slow operations *inside* an open database transaction to avoid lock contention and connection pool starvation.
- **Concurrency & Race Condition Control:** For balance mutations, quotas, or state transitions, enforce **Pessimistic Locking** (`SELECT ... FOR UPDATE`) or **Optimistic Locking** (atomic `version` increment).
- **Zero-Downtime Expand-and-Contract Migrations:** Add additive columns/tables first, deploy compatible code, backfill data, switch traffic, and drop legacy schemas only after validation.

### Gate 4: Atomic Bottom-Up Execution (Cline Memory Bank Pattern)
Implement changes strictly in structured, bottom-up layers:
1. **Layer 1:** Database Migrations & Domain Entities/Models.
2. **Layer 2:** Repository & Data Access Layer (optimized queries and locks).
3. **Layer 3:** Usecase / Service Layer (business logic, transaction boundaries, idempotency).
4. **Layer 4:** Controller / Event Consumer / DTO Validation.
5. **Layer 5:** Targeted Unit & Integration Tests.

Maintain context state using the `[PROGRESS STATE]` block across multi-turn sessions:
```text
[PROGRESS STATE]
- Completed: [Files / Layers]
- Current Active Task: [Layer / Component]
- Remaining Steps: [Remaining Layers]
```

### Gate 5: Adversarial Self-Review (Reflexion Loop / SuperClaude)
Before delivering completed code, perform a hostile self-review:
1. Did I hallucinate any import, method name, or schema field not present in the codebase?
2. Are there any N+1 queries, unindexed filters, or external network calls inside database transactions?
3. What happens if the exact same request hits the endpoint twice at the exact same millisecond?
4. Are all errors logged with actionable context and mapped to the repository's standard response format?
5. Did I break any existing caller, contract, or test within the blast radius?

---

## 4. Deterministic Bug Fixing & Root Cause Analysis (RCA) Protocol
When investigating bugs, test failures, or production incidents, trial-and-error patching is strictly forbidden.

1. **Separate Symptom from Root Cause:**
   - Do not apply superficial defensive patches (e.g. `if (x != null)` or wrapping in generic `try/catch`) without diagnosing why the state became invalid upstream.
2. **Backward Execution Trace:**
   - Trace the exact execution path from the failure/crash point backward to the entry point (`Crash Site -> Service -> Repository -> Controller/Gateway/Database`).
3. **Formulate & Prove 2–3 Technical Hypotheses:**
   - State concrete hypotheses (e.g., race condition in check-then-act, missing rollback on partial write, stale cache, DTO unmarshaling mismatch).
   - Inspect actual code lines to prove or disprove each hypothesis with `filename:line_number` evidence.
4. **Regression Audit:**
   - Audit all callers and consumers of the modified function to guarantee zero collateral breakage.

---

## 5. Mandatory Pre-Coding Scratchpad Template
```text
## [SYSTEM DESIGN & WORKFLOW PLAN]
1. Requirement & State Transitions: (Trigger -> Input -> State Change -> Output/Events)
2. Codebase Grounding & Blast Radius: (Inspected files/patterns + Impacted services/tables)
3. Workflow Sequence: (Happy Path & Failure/Compensation Path)
4. Microservice & Integration Guardrails: (API/Event Contract, Idempotency, Timeouts, Outbox/DLQ)
5. Database & Concurrency Checklist:
   - Indexes verified:
   - Anti-N+1 verified:
   - Transaction boundaries (No external I/O inside TX):
   - Locking strategy (Optimistic / Pessimistic):
6. Edge Cases Handled: (Minimum 3 concrete failure scenarios & recovery)
7. Atomic Execution Checklist: (Ordered bottom-up file layers)
```

---

## 6. Open-Source Ecosystem & Research References
To keep agent intelligence grounded and state-of-the-art:
- **Spec-Kit / Specification-Driven Development:** Emphasizes PRD/RFC-first workflows where specifications and contracts are approved before code generation.
- **Designing Data-Intensive Applications (DDIA)** (Martin Kleppmann, `https://dataintensive.net/`): Foundational principles of reliable, scalable, and maintainable systems (consensus, transactions, replication, stream processing, outbox pattern).
- **Cline & Roo-Code Memory Bank:** (`https://github.com/cline/cline`, `https://github.com/RooVetGit/Roo-Code`): Multi-turn context preservation and layered execution tracking.
- **Reflexion: Language Agents with Verbal Reinforcement Learning** (Shinn et al., `https://arxiv.org/abs/2303.11366` & SuperClaude framework `https://github.com/noahshalo/SuperClaude`): Self-reflective loops that catch logic and contract bugs before presenting code.
- **Aider Architect/Editor Architecture** (`https://aider.chat/`): Demonstrates that separating high-level architectural planning from precise file editing significantly outperforms monolithic code generation on SWE-bench.
- **Patterns of Distributed Systems** (Unmesh Joshi / Martin Fowler, `https://martinfowler.com/articles/patterns-of-distributed-systems/`): Practical blueprints for idempotency, state replication, two-phase commit, and saga patterns.
- **SWE-bench Benchmark & Best Practices** (`https://www.swebench.com/`): Empirical findings showing that thorough exploration and backward execution tracing prevent 90%+ of agent regression errors.


---

## 7. Anti-Documentation-Slop & Specification Authoring Invariants (FRD / TRD)

1. **Zero-Unchanged-Contract Dumping (Anti-Bloat):**
   - In enhancement or bugfix specifications (FRD/TRD), NEVER paste generic boilerplate request/response HTTP JSON payloads if the DTO schema did not change.
   - Dumping unchanged payloads creates false alarms for Frontend and QA engineers and pollutes the specification with irrelevant noise.
   - Mandatory statement when contracts are preserved: *"No contract changes; existing HTTP endpoint payload reused."*
2. **Delta-Only Documentation Standard:**
   - Focus 100% on what actually changed: modified internal logic, new negative response codes, altered messaging broker events (e.g. Kafka), and database migrations.
3. **Zero Sycophancy / Action-First Execution:**
   - When documentation defects or bloat are identified, execute direct remediation immediately instead of asking redundant permission.
