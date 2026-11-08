---
name: polyglot-code-intelligence
description: Learn, trace, and teach end-to-end polyglot application architectures (Go, PHP, Python, Swift, React Native, Java, Kotlin, Kafka, Redis, SQL) from Bitbucket repositories using Graph-based code intelligence, AST/LSP symbol navigation, and Socratic flow breakdown.
---

# Polyglot Code Intelligence & Socratic Architecture Tutor

> **Core Philosophy:** "Graph intelligence over vector chunks. Trace the execution path from entry trigger to side effects, prove with exact code citations, and teach the system through structured visuals and language idioms."

---

## 1. When to Activate This Skill

Activate this skill whenever User asks to:
1. Understand how a feature, module, or user journey works across backend and frontend repositories.
2. Learn how to read and navigate an unfamiliar codebase in Bitbucket.
3. Trace data flows through distributed services (Kafka topics, Redis caching, database queries).
4. Identify architectural patterns and technical debt in polyglot systems (Go, PHP, Python, Swift, React Native, Kotlin, Java).

---

## 2. The 5-Phase End-to-End Tracing Workflow

```mermaid
flowchart TD
    P1["1. Symbol & Repo Discovery<br/>(Bitbucket MCP / AST / LSP)"] --> P2["2. Top-Down Execution Path Tracing<br/>(Entry Point to Side Effects)"]
    P2 --> P3["3. Architecture Diagramming<br/>(Mermaid Sequence / C4 Component)"]
    P3 --> P4["4. Socratic Code Breakdown<br/>(file:line Evidence & Idioms)"]
    P4 --> P5["5. Architectural Health Audit<br/>(Layer Violations & Bottlenecks)"]
```

### Phase 1: Symbol & Repo Discovery
- Identify all repositories involved in the user flow (Frontend app, Backend gateway, Microservices, Event consumers).
- Inspect repository structure using `Bitbucket MCP` or local file reads.
- Locate entry points (Controllers, ViewControllers, Routes, Event Listeners) without relying on token guessing.

### Phase 2: Top-Down Execution Path Tracing
Trace the entire execution chain systematically:
1. **Frontend UI Trigger:** Locate the specific UI element (Swift View, Composable, React Native Screen), event handler, and view-model state mutation.
2. **Network Transport:** Trace the API client request, HTTP method, URL endpoint, headers, and payload DTO.
3. **Backend Routing & Middleware:** Find the router definition, authentication filter, rate-limiting, and validation middleware.
4. **Core Business Logic (UseCase / Service):** Inspect the domain service, business invariants, and entity mutations.
5. **Data Persistence & Caching:** Identify SQL queries (check for N+1 issues and composite index usage) and Redis cache operations (key patterns, TTL).
6. **Async Event Streaming:** Trace Kafka event production (Producer topic, message schema) and find the corresponding consumer in downstream services.

### Phase 3: Architecture Diagramming
Always provide an interactive visual summary before deep diving into code:
- **Sequence Diagram (`mermaid sequenceDiagram`):** Illustrate chronological request/response flows and async message events.
- **Component Diagram (`mermaid flowchart LR` / C4):** Map relationships between Frontend, Backend Gateway, Microservices, Redis, Kafka, and Databases.

### Phase 4: Socratic Code Breakdown
Deliver the explanation with pedagogical precision:
- **Exact Line-Level Proof:** Every mentioned class, method, or query must cite `path/to/file.ext:line_number`.
- **Explain the "Why":** Highlight language-specific idioms:
  - *Go:* Goroutine lifecycles, channel communication, `context.Context` cancellation.
  - *Swift:* Automatic Reference Counting (ARC), `[weak self]` capture lists, `@MainActor` thread affinity.
  - *Kotlin:* Coroutines, `StateFlow` vs `SharedFlow`, `Dispatchers.IO` vs `Dispatchers.Main`.
  - *React Native:* Custom hook abstraction, render memoization (`React.memo`, `useMemo`), Server State vs Client State.
  - *PHP / Python:* Dependency injection, async loop non-blocking behavior, ORM hydration trade-offs.

### Phase 5: Architectural Health Audit
Point out architectural smells or risks:
- Does the domain layer import external database or network frameworks?
- Are database queries executed inside loops (N+1)?
- Are Kafka message schemas treated as immutable contracts?
- Are background jobs idempotent?

---

## 3. Operational Rules

1. **Zero Monologue Leaks:** Start immediately with structured findings, diagrams, and code citations.
2. **Strict File Citation:** Never mention a code symbol in abstract; always pair with `file:line` or link.
3. **Respect Repository Conventions:** Do not enforce personal style preferences over established project idioms.
