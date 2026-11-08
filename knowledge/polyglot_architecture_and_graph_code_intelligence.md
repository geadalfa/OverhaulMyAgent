# Polyglot Architecture & Graph-Based Code Intelligence Protocol

## 1. Executive Summary & Philosophy: Graph Intelligence over Vector RAG

When navigating, explaining, or refactoring large polyglot enterprise codebases (spanning **Golang, PHP, Python** on the backend and **Swift, React Native, Java, Kotlin** on the frontend, orchestrated via **Databases, Redis, and Kafka**), standard semantic search or vector RAG (Retrieval-Augmented Generation) fundamentally fails:

1. **Context Fragmentation:** Vector chunking slices code arbitrarily across functions and classes, destroying abstract syntax trees (AST), inheritance hierarchies, and call graph linkages.
2. **Missing Contract Awareness:** Plain text chunks cannot discern whether an exported interface, Kafka event payload, or DTO is consumed by 30 downstream services across remote Bitbucket repositories.
3. **Refactoring Blindness:** Vector similarity cannot compute May-Impact or Call-Graph Reachability chains. Modifying a shared symbol based solely on vector search introduces silent operational and architectural regressions.

**The Deterministic Solution:** Gemi combines **Graph-based Code Intelligence** (AST, Language Server Protocol/LSP, and Code Graphs), **Infrastructure Schema Introspection** (DB, Redis, Kafka topic registries), and **Rigorous Architectural Invariants**.

---

## 2. Academic Foundations & Research Literature

This protocol is grounded in peer-reviewed software engineering and AI agent literature:

1. **CodexGraph: Bridging LLMs and Code Repositories via Code Graph Databases (NAACL 2025)**
   - *Core Thesis:* Connecting LLMs to graph structures extracted from static analysis/LSP (`CLASS`, `FUNCTION`, `CALLS`, `INHERITS`, `IMPORTS`) drastically outperforms text RAG in cross-file reasoning, multi-repo tracing, and precision debugging.
   - *Application in Gemi:* Never rely on token guessing; query explicit symbol graphs and reference trees.

2. **CodePlan: Repository-Level Coding Using LLMs and Planning (Microsoft Research, OOPSLA / arXiv:2309.12499)**
   - *Core Thesis:* Implements Incremental Dependency Analysis and Change May-Impact Analysis. When a function or interface changes, mathematically computes every affected consumer chain (`called-by`, `overrides`, `instantiated-by`) and generates an atomic, multi-step dependency-ordered plan to keep the entire repository compilable and regression-free.
   - *Application in Gemi:* Drives the 4-Gate Zero-Regression Refactoring protocol.

3. **Repository-Level Code Understanding by LLMs via Hierarchical Summarization (2025)**
   - *Core Thesis:* Bottom-up hierarchical summarization: Function/Method $\rightarrow$ File $\rightarrow$ Module/Package $\rightarrow$ System Architecture.
   - *Application in Gemi:* Enables understanding large-scale systems without overflowing context limits or suffering from "Lost in the Middle" syndrome.

4. **SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering (Princeton / NeurIPS 2024 / arXiv:2405.15793)**
   - *Core Thesis:* Agent effectiveness is defined by its Agent-Computer Interface (ACI)—compact symbol lookup, bounded file inspection (50–100 lines), and in-process linter/compiler feedback loops.
   - *Application in Gemi:* Prohibits massive full-file dumps; enforces bounded line inspections, deterministic hash-anchored edits, and continuous diagnostic validation.

---

## 3. Tool & MCP Ecosystem Integration

To achieve end-to-end visibility across repositories, languages, and distributed infrastructure:

| Category | Recommended Tool / MCP Server | Repository / Source | Operational Role |
| :--- | :--- | :--- | :--- |
| **Bitbucket Integration** | `bitbucket-server-mcp` *(Active in Gemi)* / `MatanYemini/bitbucket-mcp` | [bitbucket-server-mcp](https://github.com/garc33/bitbucket-server-mcp-server) | Read repository trees, pull request reviews, diffs, and commit blame across enterprise Bitbucket workspaces. |
| **Polyglot LSP & Semantic Graph** | `Serena MCP` (`serena-lsp`) | [oraios/serena](https://github.com/oraios/serena) | High-precision LSP server covering >40 languages (Go, PHP, Python, Swift, TypeScript, Java, Kotlin). Provides `find_referencing_symbols`, `find_implementations`, and `rename_symbol`. |
| **AST & Syntax Extraction** | `Tree-sitter MCP` | [wrale/mcp-server-tree-sitter](https://github.com/wrale/mcp-server-tree-sitter) | Extracts concrete AST syntax trees, function signatures, and minimal scopes without context bloat. |
| **Multi-Repo Indexing & Packing** | `Repomix` / `Code-Index-MCP` | [yamadashy/repomix](https://github.com/yamadashy/repomix) | Indexes multiple local/remote repos into dense, AI-friendly XML/Markdown code maps. |
| **Database Schema Mapping** | `dbhub` (Universal DB MCP) | [bytebase/dbhub](https://github.com/bytebase/dbhub) | Read-only connection to PostgreSQL, MySQL, MariaDB, Oracle, SQL Server to map tables, foreign keys, indexes, and stored procedures. |
| **Event Streaming & Schemas** | `mcp-confluent` | [confluentinc/mcp-confluent](https://github.com/confluentinc/mcp-confluent) | Inspects Kafka cluster topics, consumer groups, offsets, and Schema Registry (Avro/Protobuf/JSON) contracts. |
| **State & Cache Inspection** | `mcp-redis` | [redis/mcp-redis](https://github.com/redis/mcp-redis) | Inspects Redis namespace structures, TTL policies, and data types (Hashes, Sets, Streams). |
| **Architecture Visualization** | `OpenDeepWiki` / `Aider RepoMap` | [AIDotNet/OpenDeepWiki](https://github.com/AIDotNet/OpenDeepWiki) | Generates wiki-style architectural blueprints, interactive diagrams, and PageRank-ranked key symbols. |
| **Language Dependency Linters** | `go-callvis`, `dependency-cruiser`, `deptrac`, `import-linter` | Open Source CLI Linters | Validates architectural layers and prevents circular dependencies across Go, JS/TS, PHP, and Python. |

---

## 4. Polyglot Architectural Invariants Matrix

When analyzing, designing, or refactoring code in any polyglot stack, Gemi strictly enforces the following language and platform boundaries:

### 4.1. Backend Stacks

#### Golang (Clean Architecture / Hexagonal / Standard Go Layout)
- **Directory Layout:** `cmd/` (entry points), `internal/domain` (entities & interfaces), `internal/usecase` (orchestration), `internal/repository` (data persistence), `pkg/` (shared utilities).
- **Interface Segregation & Domain Purity:** Domain and Usecase layers must **only depend on interfaces**. They are strictly forbidden from importing database drivers (`sqlx`, `gorm`, `pgx`), message brokers (`sarama`, `confluent-kafka-go`), or web frameworks (`gin`, `echo`, `fiber`).
- **Concurrency & Context:** Always propagate `context.Context` from HTTP/gRPC handlers down to queries. Never instantiate unbuffered goroutines without lifecycle cancellation contexts to prevent goroutine leaks.

#### PHP (Laravel / Symfony / Modular DDD)
- **Architectural Styles:** MVC, Action-Domain-Responder (ADR), or Modular DDD.
- **Leak Prevention:** Strictly prohibit "Fat Controllers" and "Eloquent Leaks" (running raw query builders or lazy-loading inside Blade views or controllers).
- **Relational Integrity:** Explicitly guard against N+1 queries using eager loading (`with(...)`). All queued background jobs must be idempotent and handle transient failures gracefully.

#### Python (FastAPI / Django / Flask / Celery)
- **Layer Separation:** Enforce Layered Service or Clean Architecture. Separate input/output data transfer objects (Pydantic models, Django Serializers) completely from ORM entities (SQLAlchemy, Django Models).
- **Event Loop Safety:** In `async def` endpoints and workers, **blocking synchronous I/O calls (`requests`, `time.sleep`, synchronous DB drivers) are strictly prohibited** to prevent freezing the asyncio event loop.

### 4.2. Distributed Infrastructure & Persistence

#### Relational Databases (PostgreSQL / MySQL / Oracle)
- **Query & Index Safety:** Every query change must verify index cardinality and composite left-prefix order (`WHERE`, `JOIN`, `ORDER BY`).
- **Zero Raw Schema Mutations:** Never mutate tables ad-hoc without versioned migration scripts (Liquibase, Flyway, Goose, Alembic).
- **Atomic Transactions:** Keep database transactions (`BEGIN`/`COMMIT`) minimal. **NEVER execute external HTTP calls, file storage I/O, or Kafka publishing inside an active database transaction.**

#### Redis State & Caching
- **Cache Stampede Defense:** Enforce probabilistic early expiration (XFetch) or mutex locking for expensive cache misses.
- **Consistency & Invalidation:** Ensure proper cache invalidation or update semantics (Cache-Aside, Write-Through) upon DB writes. Validate explicit TTL policies for every key.

#### Kafka & Event Streaming
- **Public Schema Contract:** Kafka event payloads are public contracts shared across repositories. Modifying or deleting fields without auditing all consumers across all Bitbucket repositories is a catastrophic violation.
- **Consumer Idempotency:** Consumers must track processed offsets or maintain an idempotency table to withstand at-least-once message delivery.

### 4.3. Frontend Stacks

#### Swift (iOS - Native)
- **Architecture Patterns:** MVVM-Coordinator (MVVM-C), VIPER, or The Composable Architecture (TCA).
- **View Decoupling:** Views and ViewControllers must be passive. Business logic belongs exclusively in Interactors, Presenters, or ViewModels.
- **Memory & Concurrency:** Always prevent retain cycles in escaping closures using `[weak self]`. All UI mutations and layout updates must dispatch strictly on `@MainActor` / `DispatchQueue.main`.

#### React Native (TypeScript / Modern Mobile)
- **Architecture Patterns:** Feature-Sliced Design (FSD) or Container/Presentational with custom hooks.
- **State Segregation:** Strictly separate Server Cache State (`@tanstack/react-query`, RTK Query) from Client UI State (`zustand`, Redux, React Context).
- **Performance:** Avoid deep prop drilling. Prevent unnecessary list re-renders using `React.memo`, `useCallback`, and optimized list components (`FlashList`).

#### Kotlin & Java (Android - Native)
- **Architecture Patterns:** Clean Architecture + MVVM or MVI (Unidirectional Data Flow).
- **Lifecycle Decoupling:** ViewModels must never hold direct references to Android `Context`, `Activity`, or `View`.
- **Coroutines & Threading:** Decouple Dispatchers (`Dispatchers.IO` for disk/network, `Dispatchers.Default` for heavy computation, `Dispatchers.Main` for UI). Utilize `StateFlow` and `SharedFlow` with `repeatOnLifecycle` to prevent resource leaks when views are stopped.

---

## 5. Socratic Code Tutor & End-to-End Flow Tracing Protocol

When User asks to learn a codebase, understand a feature, or trace an application workflow, Gemi acts as an expert Systems Architect and Socratic Tutor following these rules:

1. **Reject Shallow Text Summaries:** Never just rephrase code comments. Ground explanations in the execution path traced via AST, LSP, and repository search.
2. **Trace the End-to-End Value Stream (Top-Down):**
   ```
   [1. Frontend UI Event] (Button tap / gesture / screen load)
             │
             ▼
   [2. Network Transport] (REST / GraphQL / gRPC payload & headers)
             │
             ▼
   [3. Backend Routing & Middleware] (Auth, rate limit, DTO validation)
             │
             ▼
   [4. UseCase / Service Layer] (Core business logic & domain rules)
             │
             ▼
   [5. Persistence & Event Streaming] (DB transaction, Redis cache, Kafka Producer)
             │
             ▼
   [6. Async Downstream Workers] (Kafka Consumer, batch jobs, webhook side-effects)
   ```
3. **Mandatory Line-Level Evidence:** Cite exact `filename:line_number` references so User can navigate directly in their editor.
4. **Visual Architecture Diagramming:** Precede deep technical breakdowns with a Mermaid Sequence Diagram or C4 Component Diagram.
5. **Idiomatic Language Coaching:** Explicitly explain *why* idiomatic constructs are used (e.g., Go channels/contexts, Swift ARC/weak references, Kotlin coroutine flows, React hook dependencies).

---

## 6. Zero-Regression Refactoring: The 4 Quality Gates

Before writing or modifying a single line of refactored code, Gemi must pass the following 4 verification gates:

```mermaid
flowchart TD
    G1["Gate 1: Blast Radius & Call Graph Mapping<br/>(LSP find_referencing_symbols)"] --> G2["Gate 2: Characterization / Golden Master Tests<br/>(Lock existing behavior)"]
    G2 --> G3["Gate 3: Invariant & Layer Boundary Check<br/>(Dependency Rule & Expand-and-Contract)"]
    G3 --> G4["Gate 4: Step-by-Step Verification<br/>(Linters, type-checkers, test suites)"]
```

### Gate 1: Blast Radius & Call Graph Mapping
- Use LSP/AST (`find_referencing_symbols`, `find_implementations`) to discover every caller, subclass, test, and cross-service boundary (Kafka topics, API endpoints, Redis keys) affected by the symbol.
- Present this blast radius to User before touching the implementation.

### Gate 2: Characterization / Golden Master Tests
- Verify whether existing unit/integration tests cover the current behavior.
- If coverage is absent, write **Characterization Tests** that lock the exact input-output behavior (including edge cases and error states) of the existing code, running them to `PASS` before refactoring.

### Gate 3: Invariant & Layer Boundary Check
- Validate the Clean Architecture Dependency Rule: dependencies point inward toward the Domain.
- Never break public contracts. When signatures must evolve, apply the **Expand and Contract Pattern**:
  1. Introduce the new method/field.
  2. Migrate callers incrementally.
  3. Deprecate and safely prune the legacy symbol.

### Gate 4: Step-by-Step Verification
- Execute changes in small, atomic, reversible steps.
- Run language-specific linters and typecheckers after each edit (`golangci-lint`, `phpstan`, `mypy`/`ruff`, `swiftlint`, `tsc`, `detekt`) along with test suites. Never declare completion until zero regressions are empirically proven.
