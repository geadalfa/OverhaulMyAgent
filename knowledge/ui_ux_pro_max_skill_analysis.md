# UI UX Pro Max — Design Intelligence Skill Analysis

Source: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
Version: skill 2.15.0 · CLI 2.5.0 · MIT · 147,636 stars / 15,621 forks (verified 2026-11-10)
Homepage: https://uupm.cc · Indonesian README: `README.id.md`

## 1. What it is

A large, open-source UI/UX skill for AI coding agents. It combines:
1. a searchable local design database (styles, palettes, typography, charts, UX rules, icons, stacks),
2. a deterministic Python search engine (BM25-style, standard library only, no network),
3. a design-system generator,
4. an installer CLI that writes the skill into the agent's skill directory.

It is not a UI framework and not a replacement for user research. It is a recommendation engine and checklist.

## 2. Architecture

- **Orchestrator skill:** `ui-ux-pro-max` — routes requests to design-system generation, targeted domain search, or stack rules.
- **Six sibling sub-skills:**
  - `design` — brand, tokens, UI, logo, CIP, slides, banners, icons, social photos.
  - `design-system` — primitive → semantic → component token architecture, CSS variables, scales.
  - `ui-styling` — shadcn/ui + Tailwind, accessible components, canvas-based visuals.
  - `brand` — voice, visual identity, messaging, consistency.
  - `banner-design` — social/ads/web/print banners.
  - `slides` — HTML presentations with Chart.js.
- **Engine:** `src/ui-ux-pro-max/scripts/search.py` (201 lines CLI), `design_system.py` (1,668), `core.py` (1,053), `reasoning_contract.py`.
- **Data:** CSV catalogs under `src/ui-ux-pro-max/data/`, plus `stacks/` per framework.
- **Installer:** `cli/` (Node/TypeScript, package `ui-ux-pro-max-cli`, binary `uipro`).
- **Sample app:** `stack/` — Next.js reference app with `scripts/design-audit.mjs`.

## 3. Data inventory (verified)

| Catalog | Rows | Notes |
|---|---:|---|
| Styles | 89 | 51 active, 29 supplemental, 9 deprecated → **80 searchable** |
| Color palettes | 192 | 19 columns per palette |
| Product types | 192 | Product-specific style matching |
| Typography pairings | 74 | Heading/body/mood/Google Fonts link |
| Charts | 25 | Data-viz guidance |
| UX guidelines | 120 | Accessibility, interaction, layout |
| Reasoning rules | 192 | `ui-reasoning.csv` |
| Icons | 105 | Icon guidance |
| Google Fonts | 1,934 | With license metadata |
| React performance rules | 44 | Rerender/touch-target guidance |
| Motion snippets | 17 | GSAP-oriented |
| Landing patterns | 34 | Conversion patterns |
| App-interface patterns | 32 | Mobile/app patterns |
| Tech stacks | 22 | React, Next.js, Vue, Svelte, Astro, SwiftUI, React Native, Flutter, Nuxt, shadcn, Jetpack Compose, Three.js, Angular, Laravel, JavaFX, WPF, WinUI, Avalonia, Uno, UWP, HTML/Tailwind, Nuxt UI |

The README's "80 UI styles" means active + supplemental; 9 deprecated rows remain in the CSV and should be excluded.

## 4. Workflow the skill enforces

1. **Analyze requirements** — product type, audience, style keywords, stack, platform.
2. **Generate design system** — `--design-system` aggregates product, style, color, landing, and typography matches.
3. **Targeted search** — one explicit domain (`style`, `color`, `chart`, `ux`, `typography`, `icons`, `gsap`, `react`, `web`, `google-fonts`, `landing`, `product`).
4. **Stack rules** — `--stack react|nextjs|swiftui|react-native|flutter|...`.
5. **Implement**, then run the pre-delivery checklist (icons, cursor, hover, contrast, focus, reduced motion, breakpoints).

The template includes a "Query Contract": one dominant intent per query, 2–5 meaningful terms, no unrelated checklist topics combined.

## 5. CLI reference

```bash
# Install
npm install -g ui-ux-pro-max-cli
uipro init --ai qoder          # Qoder target: .qoder/skills/
uipro init --ai qoder --dry-run
uipro update
uipro uninstall --ai qoder
```

Search examples:

```bash
python src/ui-ux-pro-max/scripts/search.py "saas dashboard" --design-system -p "My SaaS"
python src/ui-ux-pro-max/scripts/search.py "fintech onboarding" --domain style -n 5
python src/ui-ux-pro-max/scripts/search.py "focus visible" --domain ux
python src/ui-ux-pro-max/scripts/search.py "list virtualization" --stack react
python src/ui-ux-pro-max/scripts/search.py "dashboard" --design-system --persist --output-dir .
```

Useful flags: `--design-system`, `--domain`, `--stack`, `--max-results`, `--json`, `--full`, `--format ascii|markdown`, `--persist`, `--page`, `--variance 1-10`, `--motion 1-10`, `--density 1-10`, `--rtl`.

Python 3 is required; scripts use only the standard library and make no network calls. The skill explicitly tells agents not to install software on the user's machine.

## 6. Qoder support

The CLI includes Qoder as a first-class target:

- `uipro init --ai qoder` writes to `.qoder/skills/` in the project.
- Platform detection also looks for an existing `.qoder` directory.
- The generated `SKILL.md` references the installed location, not the source checkout.

Gemi has **not installed** it, because installation changes the user's skill catalog. Install only with explicit consent.

## 7. Verified behavior and caveats

Gemi ran the design-system generator from a shallow clone:

```bash
python src/ui-ux-pro-max/scripts/search.py "mental health journaling app" \
  --design-system --format markdown -p "Calm Journal"
```

Result:
- Pattern: Hero + Testimonials + CTA — a marketing landing pattern, not a journaling app flow.
- Style: **Neumorphism** — accessibility risk marked **high**.
- Primary: `#8B5CF6` (violet) — exactly the default AI purple that `ui_ux_anti_slop_design_engineering.md` prohibits.
- Typography: Lora + Raleway — plausible for wellness, but still a template match.

**Conclusion:** the generator is a useful first-draft catalog matcher, not an art director. Its output must be validated against:
1. the product's actual user journey,
2. the anti-slop constraints (neutral base, one functional accent, no default violet/indigo),
3. WCAG contrast/focus/reduced-motion,
4. brand and platform conventions.

Other caveats:
- The "basic" version is open source; brand/logo/CIP/slides premium capabilities are commercial and not fully in the repo.
- Data quality varies; font licensing must be checked per family.
- 9 deprecated styles remain in the CSV; filter `Status`.
- The repo is large; don't copy it wholesale into a project. Install via CLI when needed.
- Version metadata spans skill 2.15.0 and CLI 2.5.0; check both.
- No user research, analytics, or real-device testing is included.

## 8. How Gemi should use it

1. As a **catalog search** tool when a specific design question arises (style, palette, chart, UX rule, stack).
2. As a **first-draft design system generator** for a new project, then audit it against `ui_ux_anti_slop_design_engineering.md` and WCAG.
3. As a **checklist source** (pre-delivery checklist, interaction rules).
4. With `--persist` only when User wants a `design-system/<project>/MASTER.md`; never overwrite without `--force` and approval.
5. For User's desktop apps (DiagnoseMyDisk, ConvertMyDocuments), prefer local-first, no network, and platform-native density; do not blindly apply web landing patterns.
6. If User wants the full skill active, install with `uipro init --ai qoder` after explicit confirmation; otherwise use this knowledge doc as reference.

## 9. Relationship to existing skills

- `ui_ux_anti_slop_design_engineering.md` — negative constraints and platform density rules. This is the **gate**; Pro Max output passes through it.
- `cross_platform_uiux_qa_security_playbook.md` — QA, accessibility, and security testing.
- `app-opportunity-lab` — problem validation before design.
- `architecture-visualization` — architecture diagrams, not UI.

## 10. Links

- Repo: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- Website: https://uupm.cc
- Indonesian README: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/README.id.md
- Install docs: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/docs/INSTALL.md
- CLI: https://www.npmjs.com/package/ui-ux-pro-max-cli
