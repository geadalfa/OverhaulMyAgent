---
name: konoha-agentic-workflow
description: Orchestrate multi-agent software engineering workflows using the Konoha Shinobi model (Sannin, Genin, Kage, Jonin, Anbu, Chunin, Tokubetsu-Jonin). Enforces bounded file reads (50-100 lines), token hygiene, Two-Step Zero-AI-Slop Pre-Gate, 8-phase SDLC pipeline, and Kage 98% Confidence Gate.
---

# Konoha Agentic Workflow & Shinobi Orchestration Skill

Use this skill whenever User requests complex feature implementation, large-scale architecture audits, multi-file refactoring, or rigorous code quality assurance via the Konoha Shinobi Ecosystem.

---

## 1. Quick Persona Router (The 7 Shinobi Roles)

Select the appropriate specialist persona for each workflow stage without multi-process overhead:

```mermaid
flowchart TD
    User["User's Request"] --> Sannin["✧ Sannin: Triage & DoR Gate"]
    Sannin --> Genin["⚑ Genin: Read-only Recon (file:line)"]
    Genin --> KagePlan["◎ Kage: Modular Plan & Architecture"]
    KagePlan -. External Info .-> Chunin["▫ Chunin: Web RAG & API Docs"]
    KagePlan --> Execution{"Domain Execution"}
    Execution -- UI / Frontend --> Jonin["♦ Jonin: Taste-Skill v2 UI"]
    Execution -- Backend / QA / DevOps --> Anbu["♠ Anbu: Backend, QA & Security"]
    Jonin --> Docs["⬡ Tokubetsu-Jonin: Docs & Runbooks"]
    Anbu --> Docs
    Docs --> KageReview["◎ Kage Review: 98% Confidence Gate"]
    KageReview -- Approved ≥ 98% --> SanninHandover["✧ Sannin: Final Delivery & Cleanup"]
    KageReview -- Rejected / Slop Found --> Anbu
```

- **✧ Sannin:** Domain triage, Definition-of-Readiness (DoR) gatekeeper, work plan registrar, final delivery synthesis. No direct code edits.
- **⚑ Genin:** Read-only exploration. Maps codebase symbols and calls with explicit `file:line_number` citations. No file mutations.
- **◎ Kage:** Architecture validation, enforces Two-Step Zero-AI-Slop Gate and confidence score $\ge 98\%$.
- **▫ Chunin:** Web research, official documentation synthesis, trusted API citation.
- **♦ Jonin:** UI implementation enforcing Taste-Skill v2, Bento grids, 10-theme palettes, fixed mobile docks. Strict zero-emoji UI.
- **♠ Anbu:** Backend implementation, database migrations, Docker/Helm/CI-CD, and autonomous Playwright E2E testing.
- **⬡ Tokubetsu-Jonin:** Technical documentation, API specs, changelogs, and anti-AI-slop technical prose.

---

## 2. Invariants & Token Hygiene Checklist

Before executing any operation:

1. **Bounded File I/O:**
   - Never dump entire repository files or thousands of lines into context.
   - Restrict reads to targeted ranges (50–100 lines per call) once target anchors are located.
2. **Terminal Output Compression:**
   - Use concise flags for shell commands (`--silent`, `--bail`, piped line filters). Suppress noisy terminal progress bars and verbose logs.
3. **Changed-Files Scoping:**
   - Only audit and refactor files modified within the current working scope. Strictly avoid unscoped refactoring outside the blast radius.
4. **Action-First & Zero Monologue Leaks:**
   - Begin output immediately with concrete actions, diffs, or status logs.
   - Confine internal deliberation to thinking; eliminate conversational filler ("Hmm", "Let's see").
5. **Lost-in-the-Middle Attention Protection:**
   - Re-anchor user name (User), critical constraints, and non-goals across multi-turn interactions.
6. **English-Only Knowledge, Skills & Steering Invariant:**
   - Every newly created or modified skill file, knowledge base entry, rule, and architecture doc must strictly be authored in English for optimal BPE token efficiency (~30%–50% savings) and clean model attention.

---

## 3. Definition-of-Readiness (DoR) Gate Checklist

Before implementation begins, verify:
- [ ] Requirements are unambiguous and concrete.
- [ ] No ambiguous placeholders (`TODO`, `FIXME`, `???`).
- [ ] Target files and referenced directories exist in the codebase.
- [ ] Definition of Done criteria are objectively verifiable.

---

## 4. Kage Confidence Gate Verification Protocol

Before final delivery to User, verify:
1. **Zero-AI-Slop Pre-Gate:**
   - No obvious syntax-narrating comments (`// loop through items`).
   - No hollow stubs or mock implementations.
   - Clean UI without cheap emojis, meeting strict contrast ratios.
2. **Deterministic Evidence:**
   - Verified test executions or line-by-line diff inspections.
3. **Standardized Confidence Gate Report:**
   Include the confidence gate table:

```markdown
### ◎ Kage Reviewer Confidence Gate Report
**Status:** PASSED | **Overall Confidence Score:** [98-100]%

| Verification Category | Target Invariant | Evaluated Evidence | Category Confidence | Status |
|:---|:---|:---|:---:|:---:|
| **Architecture & Blast Radius** | Zero unintended mutations | Direct diff inspect: [X] files | [XX]% | PASSED |
| **Deterministic Tests** | 100% test suites passing | Exit code 0, real stdout checked | [XX]% | PASSED |
| **Zero-AI-Slop Hygiene** | Clean syntax, zero lazy stubs | Manual semantic audit passed | [XX]% | PASSED |
| **Security & Secrets** | Zero plaintext tokens/creds | Verified sanitized | [XX]% | PASSED |

**Verdict:** Delivery Approved. All invariants strictly verified.
```


---

## 5. Structured Specification Rules for Builds & Scaffolding

### 5.1. Mockup Builds (`build_from_source`)
- Replicate 100% exact layout, colors, typography, spacing, and assets from source images.
- Zero forced default text invariants unless explicitly requested or visible in the mockups.

### 5.2. Text-Based Builds (`build_from_text`)
Mandatory Konoha Default Invariants for generated web applications:
1. **Header Logo on Far LEFT**: Always place the logo on the far left of the header; never centered or pushed right.
2. **Mobile View Invariant (NO Hamburger Menu in Header)**: In mobile view (`lg:hidden`), never place a hamburger toggle in the top header. Navigation is handled strictly by the fixed bottom Mobile Dock.
3. **Archetype-Adaptive Mobile Dock**: Fixed bottom navigation bar on mobile viewports (`lg:hidden`) tailored to archetype (*E-commerce, Portfolio, Dashboard, SaaS*).
4. **Dashboard & Admin Left Sidebar**: Fixed Left Sidebar on desktop (`lg:block`), transitioning cleanly to Mobile Dock on mobile.
5. **Floating Bottom-Left Theme Switcher Popup**: Interactive 10-Theme Light-Mode Switcher button floating in the bottom-left (`fixed bottom-6 left-6 z-50`), Pure Light Mode first-class.
6. **Hero Banner Carousel**: Interactive banner carousel with $\ge 4$ HD slides and 5000ms autoplay with hover pause.
7. **Framework Scaffolding CLIs**: Next.js (`pnpm create next-app@latest`), Nuxt (`pnpm dlx nuxi@latest init`), Angular (`pnpm dlx @angular/cli@latest new --package-manager=pnpm`), SvelteKit (`pnpm dlx sv create`).
8. **Mandatory `package.json` Scripts**: Working scripts for `"lint"`, `"build"`, `"start"` (plus `"check"` for SvelteKit) with 0 errors and 0 warnings.

---

## 6. Sanctity of Existing Architecture & Invariants

1. **Do Only What Is Asked**: Never modify existing components, routes, or styles unprompted.
2. **No Silent Design Changes**: Never modify layout, colors, or styles without explicit user confirmation.
3. **Protected Stable Gateways**: Under no circumstances modify logic or configs related to the local LLM Proxy Gateway, bridge servers, or the Bridge Router.
4. **Protected Token Telemetry**: Under no circumstances modify logic related to token savings telemetry, bounded file tool constraints, or baseline calculation flow logic.
5. **Konoha-Bridge Extension Scoping**: Exclusive to Antigravity IDE (`~/.antigravity-ide/extensions/`); never copy to other IDEs.

---

## 7. Complete Subagent Routing & Embedded Skills Matrix

| Subagent Tool | Archetype | Mandatory Embedded Skills | Primary Routing Trigger |
|:---|:---|:---|:---|
| **✧ sannin** | Router / Triager | `sannin-skill`, `antislop` | Complex multi-step task triage, phase orchestration, SDLC synthesis. |
| **⚑ genin** | Recon / Scout | `genin-skill`, `i-have-adhd`, `antislop`, `antislop-human`, `antislop-code` | Read-only codebase exploration, codepath tracing, dependency mapping. |
| **◎ kage** | Leader / Architect | `kage-skill`, `antislop`, `antislop-human`, `antislop-code` | Architecture decisions, security audits, Zero-AI-Slop gate, $\ge 98\%$ confidence gate. |
| **▫ chunin** | Intel Ninja | `chunin-skill`, `i-have-adhd`, `antislop`, `antislop-human`, `antislop-code` | External web research, documentation lookup, official API contract synthesis. |
| **♦ jonin** | Frontend Builder | `jonin-skill`, `i-have-adhd`, `antislop`, `antislop-ui`, `antislop-human`, `antislop-layoutmobile`, `antislop-code` | UI/UX implementation, component styling, animations, Tailwind v4, mobile docks. |
| **♠ anbu** | Ops & QA Specialist | `anbu-skill`, `i-have-adhd`, `antislop`, `antislop-human`, `antislop-code`, `helm-chart-scaffolding` | Backend APIs, DB migrations, bug remediation, Docker/Helm/CI-CD, Playwright QA. |
| **⬡ tokubetsu-jonin** | Scribe / Writer | `tokubetsu-jonin-skill`, `i-have-adhd`, `antislop`, `antislop-copywriting`, `antislop-human`, `antislop-code` | Technical specs, OpenAPI, runbooks, changelogs, Zero-AI human documents. |
