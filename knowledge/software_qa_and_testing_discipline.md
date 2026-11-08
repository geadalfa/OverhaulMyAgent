# Software QA, UI State Synchronization, & Test Automation Discipline

Standard QA & software testing guidelines for Gemi to thoroughly evaluate applications (functional, architectural, UI/UX, and reactive interactions), prevent stale state bindings, and validate DOM mutations deterministically beyond mere build/lint passes.

---

## 1. Core Philosophy: Beyond Build & Lint

A successful compilation (exit code `0`) or clean `lint` pass is **NOT** proof that an application is free from runtime or functional regressions.
Most fatal UI bugs occur at the interactivity layer:
1. **Partial State Updates / Stale State Binding:** When a user switches contexts (e.g., switching disk tabs, switching accounts, filtering data), only a fraction of UI elements mutate (such as a tab border or single percentage), while the detail panel, status colors, or sub-components remain bound to stale data (`item[0]`).
2. **Silent Unhandled Exceptions in Event Handlers:** JavaScript runtime exceptions inside listener callbacks break the subsequent DOM render loop without visual feedback to the user.
3. **Destructive DOM Element ID Mutation:** Parent `innerHTML` overwrites inadvertently remove crucial ID attributes (`id="target-id"`), causing subsequent `document.getElementById(...)` invocations to return `null`.

---

## 2. AI-Native QA Frameworks, MCP Tools, & Repository Ecosystem

### 2.1. Browser & UI Testing MCP Servers
| MCP Server / Tool | GitHub Repository | Agent Capabilities & Advantages |
| :--- | :--- | :--- |
| **Playwright MCP (Official)** | `microsoft/playwright-mcp` | Uses token-efficient *Accessibility Tree* and *DOM Snapshots*. Agents programmatically click elements and verify before/after text snapshots. |
| **ExecuteAutomation Playwright MCP** | `executeautomation/mcp-playwright` | Provides API testing, screenshot diffing, and automated console error capture. |
| **Chrome DevTools MCP** | `ChromeDevTools/chrome-devtools-mcp` | Direct connection to the *Chrome DevTools Protocol (CDP)* for live DOM inspection, event listeners, network tracing, and runtime evaluation. |

### 2.2. AI-Native E2E & Visual Testing Frameworks
- **antiwork/shortest (`github.com/antiwork/shortest`):** Playwright-based E2E testing using Natural Language Assertions.
- **web-infra-dev/midscene (`github.com/web-infra-dev/midscene`):** Visual UI testing using Vision-Language Models (VLMs) to detect visual state mismatches (e.g., text displays "96% Good" but badge background remains red due to stale CSS classes).
- **browserbase/stagehand (`github.com/browserbase/stagehand`):** Browser primitives (`act()`, `extract()`, `observe()`) paired with Playwright to extract UI payloads and assert against backend ground-truth APIs.
- **magnitudedev/magnitude (`github.com/magnitudedev/magnitude`):** Autonomous AI testing framework for exploring application workflows and validating regression invariants.

### 2.3. Curated QA Repositories
- `TheJambo/awesome-testing`: Comprehensive curation of functional testing, UI regression, and mutation testing tools.
- `awesomelistsio/awesome-test-automation` & `awesomelistsio/awesome-qa`: Cross-platform testing libraries and assertion frameworks.
- `PatrickJS/awesome-cursorrules` & `e-gov/cursor-prompts`: Curated prompts and verification gates for autonomous coding agents.

---

## 3. SFDPOT Testing Heuristic (James Bach / Ministry of Testing)

Every software audit evaluates 6 heuristic dimensions:
1. **Structure:** Codebase modules, binary directories, config files, static assets, bundling.
2. **Function:** What does the system do? Calculation validation (metrics, offsets, latency), system remediation (TRIM/CHKDSK), localization, theme toggling.
3. **Data:** API JSON payloads, boundary conditions (0%, 100%, 2TB vs 120GB drives, missing S.M.A.R.T attributes, offline cache vs live WMI).
4. **Platform:** Windows 10/11, Edge App Mode, Chrome App Mode, macOS, Administrator/root elevation vs standard permissions.
5. **Operations:** User interaction flows: rapid clicks, rapid tab switches, start/pause/resume scan cycles, clearing terminal logs.
6. **Time:** Asynchronous latency, polling intervals, cache pre-warming, heartbeat timeouts (preventing orphaned background zombie processes).

---

## 4. UI State Synchronization Gate (Mandatory for Multi-Item UI)

When building or refactoring components with multi-item selection (disk tabs, dropdowns, master-detail tables):

```markdown
### UI State Synchronization Checklist
1. State & Reactivity Audit:
   - Ensure the active identifier (`activeDiskIndex` / `selectedItem`) propagates to ALL detail sub-components, not merely the header or a single badge.
   - Prohibit hardcoded indices (`items[0]`) in detail views, badge color lookups, warning alerts, and metric panels.
   - Maintain element ID integrity: avoid destructive parent `innerHTML` wipes that eliminate child element IDs.
2. Dynamic Selection Verification:
   - Select Item 1 -> Capture full snapshot (Title, Serial, Capacity, Badge Color, Warning Banner, Metrics Table).
   - Select Item 2 through Item N -> Verify ALL snapshot fields mutate proportionally according to the active item's payload.
   - Reselect Item 1 -> Verify Item 1 restores pristine state without residual data from intermediate items.
3. Console & Network Hygiene:
   - Verify zero `TypeError: Cannot read properties of undefined/null` in browser console logs during transitions.
   - Verify API calls transmit the active item identifier (e.g., `/api/scan_chunk?disk_index=3` when disk 4 is selected).
```

---

## 5. Automated Headless CDP Testing Protocol

When dedicated test frameworks are not pre-installed, agents run deterministic E2E assertions via native headless browsers using the Chrome DevTools Protocol:
```bash
# Windows Edge App Mode
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --remote-debugging-port=9222 "http://127.0.0.1:5550"

# macOS Chrome Headless
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless=new --remote-debugging-port=9222 "http://127.0.0.1:5550"
```
And evaluate JavaScript via WebSocket/CDP to:
- Assert DOM node text via `document.getElementById('...')`
- Verify tab switches and active CSS classes
- Ensure `window.addEventListener('error')` logs zero unhandled exceptions.
