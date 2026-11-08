# Noted Connected Workspace Architecture & Knowledge Engine

> **Live Production System:** [noted-alpha-eight.vercel.app](https://noted-alpha-eight.vercel.app/?pageId=page-welcome)  
> **Core Architecture:** All-in-One Connected Workspace (Notion-inspired Block-Tree, Multi-View Database, Offline-First Vault, and Bidirectional Network Backlinks).  
> **Engineering Origin:** Synthesized from REA reverse-engineering analysis of Notion Desktop (v7.39.0 macOS DMG package), local Electron SQLite patterns, and high-performance Web APIs.

---

## 1. System Overview & The Connected Workspace Paradigm

`noted` is an offline-capable, highly responsive connected workspace application designed to replace fragmented note-taking, task tracking, and database tools with a single unified, block-based reactive canvas:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        NOTED WORKSPACE TOPOLOGY                        │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │                  BLOCK-TREE EDITING CANVAS                     │   │
│   │  • Breadcrumb    • Callout      • Headings (H1/H2/H3)          │   │
│   │  • To-Do Check   • Bullet List  • Numbered List • Toggle       │   │
│   │  • Code Block    • Math (LaTeX) • Web Bookmark  • Video Embed  │   │
│   │  • Quote         • Dividers     • Page Backlinks ([[page:...]])│   │
│   └────────────────────────────────┬───────────────────────────────┘   │
│                                    │                                   │
│   ┌────────────────────────────────▼───────────────────────────────┐   │
│   │                 MULTI-VIEW DATABASE ENGINE                     │   │
│   │  • Grid / Table View    • Kanban / Board View (Dynamic Group)  │   │
│   │  • Timeline / Gantt Bar • Dynamic Cell Types (Text/Date/Status)│   │
│   └────────────────────────────────┬───────────────────────────────┘   │
│                                    │                                   │
│   ┌────────────────────────────────▼───────────────────────────────┐   │
│   │           RESILIENT DUAL-TIER STORAGE & LIVE SYNC              │   │
│   │  • IndexedDB Vault (`noted_offline_vault_v1`)                  │   │
│   │  • OS Persistent Storage (`navigator.storage.persist()`)      │   │
│   │  • Cross-Tab Realtime Sync (`BroadcastChannel`)                │   │
│   │  • Google Cloud OAuth + Guest Vault Partitioning               │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Pillar 1: The Hierarchical Block-Tree Data Model

In `noted`, every document is not a flat string of text; it is an ordered tree of typed, addressable **Block objects**:

### 2.1. Block Schema Specification
```typescript
interface Block {
  id: string;               // Unique block identifier (e.g. "b-callout-1", "b-todo-2")
  type: BlockType;          // Discriminator string
  text?: string;            // Text payload or title
  icon?: string;            // Emoji or icon badge
  color?: string;           // Color theme token (e.g. "blue", "green", "orange")
  checked?: boolean;        // Checked state for to_do blocks
  isOpen?: boolean;         // Expansion state for toggle blocks
  subtext?: string;         // Expanded body text for toggle blocks
  language?: string;        // Language identifier for syntax-highlighted code blocks
  code?: string;            // Code snippet body
  content?: string;         // Raw KaTeX LaTeX expression for math blocks
  url?: string;             // URL destination for bookmark or video embeds
  domain?: string;          // Extracted domain name for bookmark preview
  caption?: string;         // Descriptive caption for media/bookmark blocks
  targetPageId?: string;    // Referenced page ID for bidirectional link_to_page
  targetTitle?: string;     // Referenced page title cache
  targetIcon?: string;      // Referenced page icon cache
  headers?: string[];       // Column names for table / database blocks
  columnTypes?: string[];   // Column data types ("text" | "status" | "date" | "number")
  rows?: string[][];        // Row cell matrices for database records
  viewType?: "table" | "board" | "timeline"; // Active layout view for database
  groupByCol?: number;      // Column index used for dynamic Kanban grouping
}
```

### 2.2. Block Type Catalog
1. **Callout (`callout`):** Highlight boxes with custom icons and semantic background colors for important notes, architectural decisions, and warnings.
2. **Interactive Checklists (`to_do`):** Action items with instant strike-through styling and state persistence.
3. **Collapsible Toggles (`toggle`):** Expandable disclosure blocks designed to keep large specifications and technical documentation clean and digestible.
4. **Code Engine (`code`):** Monospace syntax-highlighted blocks with language selector and one-click clipboard copy.
5. **Mathematical Engine (`math`):** Formatted LaTeX formulas rendered with KaTeX (e.g., probability densities, financial volatility formulas, algorithmic proofs).
6. **Smart Web Bookmarks (`bookmark`):** Dynamic cards with auto-extracted page titles, descriptions, favicons, and domains.
7. **Bidirectional Page Links (`link_to_page`):** Hyperlink nodes formatted as `[[page:<pageId>|<PageTitle>]]` or `@mention` that create a living semantic graph across workspace pages.

---

## 3. Pillar 2: Multi-View Dynamic Database Engine

`noted` elevates simple tables into relational database views:

### 3.1. Database View Modes
1. **Table View (`viewType: "table"`):**
   - Traditional rows and columns for spreadsheet-like entry.
   - Column-type enforcement (`text`, `status`, `date`, `number`).
   - Dynamic cell editing and row addition.
2. **Board / Kanban View (`viewType: "board"`):**
   - Automatically pivots rows into Kanban columns grouped by a chosen category or status column (`groupByCol`).
   - Drag-and-drop card movement across stages (e.g., `Planned` -> `In Progress` -> `Completed`).
3. **Timeline View (`viewType: "timeline"`):**
   - Evaluates start and end date columns to render chronological Gantt bars.
   - Computes dynamic percentage widths and left offsets along a multi-month project horizon.

---

## 4. Pillar 3: Resilient Dual-Tier Storage & Live Sync Architecture

A key lesson reverse-engineered from Notion Desktop and local-first architecture is **Zero Data Loss**:

### 4.1. Dual-Tier Persistence
1. **IndexedDB Object Store (`noted_offline_vault_v1`):**
   - Stores workspace blobs, serialized page trees, and media assets in a dedicated `workspace_blobs` object store.
   - Survives browser cache clears and offline conditions.
2. **OS Persistent Storage API (`navigator.storage.persist`):**
   - Programmatically requests durable persistence from the browser runtime.
   - Prevents operating systems and browser engines from evicting workspace databases under disk pressure.
3. **Fast LocalStorage L1 Cache (`noted_pages_v2` & `noted_trash_v2`):**
   - Instant synchronous retrieval for boot-up and sub-millisecond page transitions before IndexedDB finishes hydrating.

### 4.2. Zero-Latency Realtime Cross-Tab Live Sync
- Utilizes the browser's native `BroadcastChannel` API (`noted_live_sync_v1`):
  ```javascript
  const channel = new BroadcastChannel("noted_live_sync_v1");
  channel.postMessage({
    type: "LOCAL_TAB_MUTATION",
    tabId: currentTabId,
    timestamp: Date.now(),
    pageId: modifiedPageId,
    mutation: blockTreeDelta
  });
  ```
- Any edits, block reorders, or comments made in Tab A instantly propagate to Tab B without network roundtrips or server dependencies.

---

## 5. Pillar 4: Collaborative Comments & Context Threading

`noted` introduces granular, contextual review threads:
1. **Block-Level Anchoring:** Comments can attach directly to a specific block ID (`blockId: "b-callout-1"`), keeping discussion anchored to the exact paragraph, code block, or database row.
2. **Page-Level Threads:** General discussion attached to `pageId` for high-level reviews.
3. **Threaded Replies & Author Identity:** Nested conversation replies, author avatars (`avatar: "D"`), color badges, and relative human timestamps (`"Baru saja"`, `"5m lalu"`, `"1h lalu"`).
4. **Resolution Tracking:** Resolved threads can be toggled without data loss, maintaining a full audit trail of architectural discussions.

---

## 6. Pillar 5: Learnings from Notion Desktop Reverse Engineering (REA Analysis)

During the reverse-engineering analysis of the Notion Desktop application (v7.39.0 macOS DMG package):
1. **Sub-Millisecond Input Latency Invariant:** Block editors must separate user typing from persistence. Keystrokes mutate the in-memory tree immediately; disk persistence is debounced (300ms) to ensure zero input lag.
2. **SQLite Schema Partitioning:** Notion structures its local database with separated tables: `spaces`, `blocks`, `comments`, and `users`. `noted` mirrors this normalized representation within its IndexedDB vault.
3. **MCP Worker Integration Readiness:** Designed to expose workspace pages, block trees, and database queries as tools over the Model Context Protocol (MCP), allowing AI agents to read and modify workspace pages programmatically.

---

## 7. How Noted Enhances Gemi's Intelligence & Cognitive Architecture

Integrating the Noted paradigm elevates Gemi's problem-solving capabilities:
1. **Block-Tree Thought Structuring:** Instead of generating monolithic walls of text, Gemi models complex software architectures, PR reviews, and sprint plans into modular blocks (Callouts, Headings, Toggles, Code, Tables, and Math).
2. **Multi-View Project Tracking:** Gemi can represent project deliverables simultaneously as detailed specifications (text blocks), tabular matrices (Table view), and delivery pipelines (Board / Kanban view).
3. **Bidirectional Knowledge Graph:** Connecting concepts with `[[page:...]]` backlinks ensures that related modules, bug investigations, and architectural decision records (ADRs) form an interconnected knowledge graph rather than siloed files.
4. **Zero Data Loss Discipline:** Emulating Noted's dual-tier persistence safeguards state, session context, and critical engineering invariants across multi-turn interactions.
