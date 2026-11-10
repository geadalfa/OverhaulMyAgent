# UI/UX Anti-AI Design Engineering Protocol

> **Reference Context:** Distilled from Gemini Argon analysis, industry design engineering standards (Linear, Vercel, Apple HIG, Raycast), and anti-slop repositories (`miqdadbadjuber/anti-slop`, `dickwu/apple-design-skill`, `emilkowalski/skills`, `spencergoldade/cursor-designer`).

---

## 1. The Anatomy of "AI Slop" in UI/UX

LLMs suffer from statistical regression to the mean of their training dataset. When asked to generate frontends without strict constraints, they consistently produce generic, recognizable patterns termed **AI Slop**:

| Slop Pattern | Why AI Does It | Human Engineering Solution |
| :--- | :--- | :--- |
| **Purple/Indigo Gradients** | `indigo-500` to `purple-600` is the statistical median in Tailwind open-source code. | Enforce neutral foundational palettes (Zinc, Slate, Stone, OKLCH) for 90% of surfaces; 1 solid, purposeful accent color. |
| **Inter / Roboto Everywhere** | Default fallback in modern CSS boilerplates. | Deliberate typography pairing (e.g., Geist Sans, Plus Jakarta Sans, Switzer) with strict weight and tracking hierarchy. |
| **Treating Desktop Like a Web Landing Page** | Training data is heavily skewed toward marketing websites with full-page fluid document scroll. | Fixed App Shell (`100vh`, `overflow-hidden`), distinct multi-pane containers, localized scrolling inside internal panels/tables only. |
| **Superficial Hierarchy (Font Sizing Only)** | AI increases font size (`text-4xl`, `text-2xl`, `text-lg`) instead of refining contrast and optical weight. | Refine hierarchy via font-weight (`font-medium` / `font-semibold`), letter spacing (`tracking-tight` on headings), and tonal contrast (`text-zinc-900` vs `text-zinc-500`). |
| **Glow, Sparkle Badges & Fake Terminals** | AI defaults to sci-fi/crypto aesthetics as shorthand for "modern". | Functional, purpose-driven surfaces; remove ornamental glow effects and unnecessary border gradients. |

---

## 2. Architecture & Design Contracts: `AGENTS.md` vs `DESIGN.md`

Modern engineering separates **architectural behavior** from **design tokens**:

```
project-root/
├── AGENTS.md        <-- Behavioral guardrails, negative constraints, workflow rules
├── DESIGN.md        <-- Machine-readable design tokens (YAML/CSS/Tailwind tokens)
└── src/
```

### 2.1. The Role of `DESIGN.md`
`DESIGN.md` lives at the project root and acts as the single source of truth (SSOT) for visual tokens:
- **Color Palettes & Surface Tokens:** Surface base (`background`, `surface-1`, `surface-2`), border definitions (`border-subtle`, `border-strong`), text layers (`text-primary`, `text-secondary`, `text-muted`), and accent/brand tokens.
- **Typography Scale:** Explicit font families, font sizes, line heights, letter tracking (`tracking-tight`), and tabular figures (`tabular-nums`).
- **Spacing, Radius & Shadows:** 4px/8px grid system, consistent `rounded-*` scale, and subtle border-elevation pairs instead of heavy drop shadows.

### 2.2. Guardrail Enforcement
Before generating or modifying any UI component, the agent must inspect `DESIGN.md` and use established tokens rather than ad-hoc inline hex codes or arbitrary utility classes.

---

## 3. Essential Ecosystem: Repositories & Tools

### 3.1. GitHub Repositories & Skills
- **`miqdadbadjuber/anti-slop`**:
  - Purpose: Negative filter rulebook blocking AI clichés (sparkle badges, faux terminal blocks, rainbow card borders, hyperbolic placeholder text).
  - Installation: `npx antislop-ai` or `npx skills add miqdadbadjuber/anti-slop`.
- **`dickwu/apple-design-skill`**:
  - Purpose: Synthesizes 123 pages of Apple Human Interface Guidelines (HIG) for cross-platform apps (Tauri, Electron, SwiftUI, Flutter, React Native).
  - Core Focus: Native window framing, collapsible sidebars, unified toolbars, proper information density, and macOS/iOS ergonomics.
- **`emilkowalski/skills`**:
  - Author: Emil Kowalski (Design Engineer at Linear & Vercel).
  - Core Focus: Design taste, physics-based spring animations, zero-delay `pointer-down` interaction feedback, optical alignment, and tactile polish.
- **`jakubkrehel/skills` & `make-interfaces-feel-better`**:
  - Purpose: Optical balancing, natural OKLCH color palettes, harmonious hover transitions, and perceived performance enhancements.
- **`spencergoldade/cursor-designer`**:
  - Purpose: Modular design rulesets (`ui-layout-and-density.mdc`, `ui-visual-language.mdc`, `ia-navigation-and-structure.mdc`, `cross-platform-ux-consistency.mdc`).

### 3.2. Web Directories & Registries
- **DesignMD Directory (`designmd.directory`)**: Ready-to-use `DESIGN.md` token sets reverse-engineered from world-class software (Linear, Vercel, GitHub, Raycast, Cursor).
- **CSS DNA (`cssdna.com`)**: Tool for extracting computed styles (color distributions, font hierarchy, radii, shadows) from reference applications into structured `DESIGN.md` YAML blocks.
- **Skills.sh (`skills.sh`)**: Open registry for agent skills (e.g., `npx skills add shadcn/ui`).

### 3.3. UI/UX Model Context Protocol (MCP) Servers
- **21st.dev MCP (`21st.dev/mcp`)**: Catalog of modern UI components built by human design engineers. CLI: `npm i -g @21st-dev/cli`.
- **shadcn/ui Official MCP (`ui.shadcn.com/docs/mcp`)**: Connects to the shadcn registry, custom themes, and Radix/Base UI accessible primitives via `npx shadcn@latest mcp`.
- **Figma Official MCP Server (`mcp.figma.com/mcp`)**: Two-way design synchronization—inspects Figma frames, token variables, and Auto Layout, with `code-to-canvas` capability.

---

## 4. Multi-Platform Guardrails Matrix

| Dimension | Desktop Applications (Tauri / Electron / Native) | Web Applications (SaaS / Dashboard / Portals) | Mobile Applications (React Native / Flutter / Native) |
| :--- | :--- | :--- | :--- |
| **Viewport & Scroll** | **Fixed App Shell (`100vh`, `overflow-hidden`)**. Window does not scroll. Only localized data containers (tables, list views, detail panels) have scrollbars. | **Fluid Document or Split Shell**. Marketing/public pages scroll naturally; dashboard sections use a bounded split shell (`max-w-7xl` container). | **Single-Column Stack**. Mandatory adherence to Safe Area Insets (status bar, notch, dynamic island, home indicator). |
| **Information Density & Typography** | **High Density**. Body text: `12px–13px` (`0.8125rem`). Button heights: `28px–32px`. Grid gaps and padding: `8px–12px`. | **Medium Density**. Body text: `14px–16px`. Button heights: `36px–40px`. Whitespace: `16px–24px`. | **Touch-First Density**. Body text: `15px–16px` (prevents iOS form auto-zoom). Minimum touch target: `44x44px`. |
| **Navigation Patterns** | Collapsible left sidebar, Command Palette (`Cmd/Ctrl + K`), full keyboard navigation (`Tab`, `Esc`, arrow keys), **zero website footers**. | Top navigation bar or left sidebar, breadcrumbs for deep hierarchies, browser back-forward & URL deep-linking. | Bottom Tab Bar (max 4–5 destinations), swipe-back gestures, **Bottom Sheets** instead of centered modal dialogs. |
| **Surfaces & Color** | Surface layering with subtle 3%–5% contrast deltas, 1px low-opacity borders (`border-white/10` or `border-black/5`), minimal drop shadows. | Neutral canvas with 1 solid brand accent color for Primary CTAs (max 10% screen surface). | High outdoor contrast, active touch state feedback (`active:scale-[0.97]`), native haptic triggers. |

---

## 5. Anti-AI Color & Typography Specification

### 5.1. Negative Constraints for Colors
1. **Strictly Prohibit AI Default Hues:** Never use `indigo-500`, `purple-600`, `violet-500`, or purple-to-blue gradients unless explicitly requested in the client spec.
2. **Neutral Base Dominance (90% Rule):** 90% of surfaces must be derived from neutral monochrome scales: `Zinc`, `Slate`, `Stone`, or perceptually uniform `OKLCH` scales.
3. **Single Functional Accent (10% Rule):** Use exactly one accent color reserved exclusively for primary interactive triggers, active navigation markers, or critical status indicators.

### 5.2. Typography Refinement Rules
1. **Never Differentiate by Size Alone:** Combine font weight (`font-medium` or `font-semibold`), letter spacing, and tone.
2. **Letter Spacing Discipline:**
   - Display/Headings: `tracking-tight` or `-0.02em` to prevent loose, amateur headers.
   - Body & Small Labels: `tracking-normal` or `tracking-wide` (for uppercase tags: `text-xs uppercase tracking-wider font-semibold`).
3. **Tabular Numerics:** Enforce `tabular-nums` (`font-variant-numeric: tabular-nums` or Tailwind `tabular-nums`) for all tables, counters, prices, and metrics so numbers stay horizontally aligned across state updates.

### 5.3. Recommended Modern Typefaces (Replacing Default Inter)
- **Desktop & Technical Dashboards:**
  - Primary UI: *Geist Sans*, *Plus Jakarta Sans*, *Switzer*, *General Sans*.
  - Monospace/Code: *Geist Mono*, *JetBrains Mono*.
- **Editorial / Consumer Products:**
  - Primary UI: *Instrument Sans*, *Satoshi*, *Cabinet Grotesk*.

---

## 6. Component Quality Checklist
Before declaring any UI task complete, perform an adversarial self-audit:
- [ ] Is the desktop window scroll-locked with `overflow-hidden`?
- [ ] Are buttons sized compactly (`28-32px` desktop, `44px` mobile)?
- [ ] Are borders subtle 1px low-opacity lines instead of harsh black/gray boxes?
- [ ] Is keyboard navigation fully functional (`Esc` dismisses, `Enter` submits, `Tab` cycles)?
- [ ] Are numeric metrics configured with `tabular-nums`?
- [ ] Is the color palette grounded in neutral tones without generic purple gradients?
- [ ] Are touchable mobile elements sized at least 44x44px?

---

## 7. Complementary: UI UX Pro Max

For catalog search and first-draft design-system generation, see `ui_ux_pro_max_skill_analysis.md` (MIT skill with 80 searchable styles, 192 palettes, 74 font pairings, 25 charts, 120 UX rules, 22 stacks; Qoder install target `.qoder/skills/`).

Treat its output as a **draft**, not a decision. The generator can propose violet/indigo palettes and high-risk styles such as Neumorphism; validate every recommendation against the anti-slop constraints in this document and WCAG 2.2 before implementation.
