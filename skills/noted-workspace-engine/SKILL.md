---
name: noted-workspace-engine
description: Structure engineering architectures, project roadmaps, and multi-view database schemas (Table, Board/Kanban, Timeline) using the Noted block-tree connected workspace paradigm, with offline vault persistence and bidirectional backlinks.
---

# Noted Connected Workspace Engine Skill

This skill operationalizes the connected workspace architecture of **Noted** (`https://noted-alpha-eight.vercel.app/?pageId=page-welcome`), allowing Gemi to represent system designs, product roadmaps, task boards, and research syntheses using Notion-grade block trees and relational multi-view databases.

---

## 1. When to Activate This Skill

Activate this skill whenever:
- Designing or presenting complex multi-phase software roadmaps, sprint plans, or engineering backlogs.
- Structuring technical specifications, architecture decision records (ADRs), or reading syntheses.
- Modeling data that benefits from multiple dynamic perspectives (tabular data, Kanban boards, Gantt timelines).
- Implementing resilient, offline-first client architectures (IndexedDB vaults, storage quota persistence, and cross-tab BroadcastChannel sync).

---

## 2. Core Protocol 1: Block-Tree Atomic Representation

Represent specifications not as monolithic text, but as an ordered hierarchy of typed blocks:

### 2.1. Standard Block Primitives
- **Callout Block (`callout`):**
  Use for architectural warnings, executive summaries, or design constraints.
  ```markdown
  > 💡 **Core Objective:** Establish sub-millisecond local block store persistence.
  ```
- **Checklist Block (`to_do`):**
  Use for verified action items, delivery gates, and test suites.
  ```markdown
  - [x] Reverse-engineer Electron bundle architecture
  - [ ] Implement IndexedDB blob storage provider
  ```
- **Collapsible Toggle (`toggle`):**
  Wrap deep technical implementation details, raw JSON schemas, or long command sequences inside disclosure blocks.
  ```markdown
  <details>
  <summary>Click to expand technical payload schema</summary>
  
  ```json
  { "pageId": "page-welcome", "version": 2 }
  ```
  </details>
  ```
- **Mathematical Formula (`math`):**
  Use formatted KaTeX blocks for algorithmic complexity, financial models, or quantitative logic:
  $$f(x) = \frac{1}{\sigma \sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}$$
- **Bidirectional Backlinks (`link_to_page`):**
  Connect related technical notes using `[[page:<page-id>|<Page Title>]]` format to maintain an interconnected knowledge graph.

---

## 3. Core Protocol 2: Multi-View Dynamic Database Schemas

When presenting project tasks or tabular resources, format them so they can be consumed across 3 primary views:

### 3.1. Grid / Table View
Strict column data typing (`text`, `status`, `date`, `number`):

| Task / Feature | Category | Owner | Status | Target Date |
| :--- | :--- | :--- | :--- | :--- |
| Block-based Editor Core | Architecture | Dani | Completed | 2026-10-15 |
| Dynamic Kanban Views | UX | Dani | In progress | 2026-10-30 |
| IndexedDB Vault Engine | Storage | Platform | Planned | 2026-11-15 |

### 3.2. Board / Kanban View (Pivoted by Status / Category)
Group items into explicit operational lanes to visualize work-in-progress (WIP):
- **Planned:** IndexedDB Vault Engine, End-to-End Encryption
- **In Progress:** Dynamic Kanban Views, Realtime Collaborative Sync
- **Completed:** Block-based Editor Core, Slash Commands, Markdown Export

### 3.3. Timeline / Gantt View
Sequence items along temporal dependency horizons:
- `Q1 (Oct - Dec 2026):` Core Block Engine & Local Offline Vault
- `Q2 (Jan - Mar 2027):` Multi-View Databases & Live Sync Bus
- `Q3 (Apr - Jun 2027):` MCP Worker Integration & Native Electron Wrappers

---

## 4. Core Protocol 3: Resilient Offline-First Vault & Live Sync Architecture

When building or architecting web/desktop applications for User, enforce Noted's storage invariants:

1. **Dual-Tier Storage Strategy:**
   - **L1 Synchronous Cache:** Fast LocalStorage for instantaneous boot-up and window titles.
   - **L2 Durable Object Store:** IndexedDB (`noted_offline_vault_v1`, object store `workspace_blobs`) storing serialized documents, media blobs, and audit logs.
2. **OS Persistent Storage Protection:**
   - Execute `navigator.storage.persist()` on app bootstrap to prevent browser disk cleanup eviction.
3. **Zero-Latency Cross-Tab Sync:**
   - Utilize `BroadcastChannel` (`noted_live_sync_v1`) to dispatch `LOCAL_TAB_MUTATION` events across tabs without polling or server latency.

---

## 5. Core Protocol 4: Contextual Comment Threading

Enforce contextual discussion threading during code reviews and architectural planning:
- **Block-Anchored Commentary:** Anchor feedback to specific block IDs (`blockId: "b-callout-1"`) rather than general page comments.
- **Resolution Lifecycle:** Track threads through `Open` -> `In Review` -> `Resolved` states with timestamps and author attribution.
