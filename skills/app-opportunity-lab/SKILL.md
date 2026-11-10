---
name: app-opportunity-lab
description: Use when User wants to brainstorm, validate, design, or build a desktop, web, or mobile app that solves a real problem — especially in finance, psychology/mental health, productivity, pet care, or daily life. Combines problem discovery, domain ethics, UI/UX, architecture, QA, security, and business viability into one workflow.
---

# App Opportunity Lab

Turn a problem User cares about into a validated app concept and a build plan — without hype, harm, or wasted effort.

## When to activate

- "Saya mau bikin aplikasi untuk …"
- "Bantu brainstorming ide aplikasi …"
- "Aplikasi ini masalahnya apa, layak tidak?"
- "Rancang MVP untuk …"
- "Gabungkan finance/psikologi/UI/UX jadi satu produk."

## Non-negotiables

1. **Problem first** — observed behavior and current workaround, not imagined demand.
2. **Domain gates** — finance licensing, psychology safety, privacy, and security are checked before design.
3. **No diagnosis, no personalized investment advice, no unauthorized security testing.**
4. **Deterministic math and cited facts** — never invent rates, returns, or clinical claims.
5. **Local-first** for sensitive data; sync only when it creates real value.
6. **Evidence before polish** — prototype and test with 5 users before building.

## Workflow

### 0. Frame

Restate the problem in one sentence and name the target user. If either is vague, run discovery first.

### 1. Discover

- Interview for past behavior, not hypotheticals.
- Map the current workaround and its cost.
- Quantify frequency, severity, willingness to pay.

**Output:** problem statement + 3 evidence quotes + current workaround.

### 2. Define

- Write the job-to-be-done.
- Choose one narrow segment.
- Run the domain gates.
- Set success metrics.

**Output:** one-pager (see template below) + gate checklist.

### 3. Choose platform

Use the matrix in `app_opportunity_lab_playbook.md`:
- Heavy local files/processing/privacy → desktop.
- Reach/collaboration → web.
- Daily capture/notifications → mobile.
- Hybrid is allowed: desktop engine + local web UI.

### 4. Design UX

- One core loop, four states per async action, keyboard-first on desktop, touch-first on mobile.
- Accessibility and localization from day one.
- Prototype and test with 5 users; measure task success.

**Output:** flow diagram + prototype + usability notes.

### 5. Architecture

- Data model, local storage, sync, integrations, auth.
- Privacy boundaries and retention.
- Failure modes and offline behavior.
- Use `architecture` skill for ADRs and trade-offs.

**Output:** C4 context/container + ADR + data flow.

### 6. QA and security

- Test pyramid: unit, integration, E2E.
- Threat model (STRIDE), authZ matrix, input validation, update integrity.
- Platform-specific checks: Windows signing, macOS notarization, web CSP, mobile MASVS.
- Release gate before beta.

**Output:** test plan + threat model + release checklist.

### 7. Business model

- Pick one: subscription, freemium, transaction fee, marketplace, B2B.
- Compute CAC, LTV, payback, burn, runway.
- Check regulatory constraints for finance/payments.

**Output:** unit economics + pricing hypothesis.

### 8. MVP and validation

- In scope: one core loop that proves the value.
- Out of scope: everything else.
- Beta cohort, retention, task success, willingness to pay.
- Decide: double down, pivot, stop.

**Output:** MVP spec + validation scorecard + decision.

## Domain routing

| Need | Read / use |
|---|---|
| UI/UX, QA, testing, pentest | `cross_platform_uiux_qa_security_playbook.md` |
| Finance, economics, unit economics | `finance_economics_macro_micro_map.md` + `holistic_financial_agent_intelligence.md` |
| Psychology, mental health, animal behavior | `psychology_mental_health_and_modern_problems.md` |
| Method, scorecard, templates | `app_opportunity_lab_playbook.md` |
| Repo learning / architecture tracing | `repo-architecture-mentor` |
| Architecture decision records | `architecture` skill |
| Codebase research report | `researching-codebase` skill |
| UI implementation | `anti-slop-ui-design` |
| Testing discipline | `software-qa-and-ui-testing` |
| Safe refactor | `zero-regression-refactoring` |

## Opportunity scorecard

Score 1–5, weighted:

- Severity 25%
- Frequency 20%
- Willingness to pay 15%
- Feasibility 20%
- Differentiation 10%
- Safety/ethics fit 10%

**Build only if weighted score ≥ 3.8 and no domain gate is violated.** Subtract a risk penalty (0–2) for unresolved harm.

## One-pager template

```markdown
# <App name>
## Problem (observed, with evidence)
## User segment
## Job-to-be-done
## Current workaround and cost
## Solution (one core loop)
## Platform choice and why
## Evidence base
## Risks and ethics
## Success metrics
## MVP scope (in / out)
## Business model
```

## Safety escalation

If the idea touches self-harm, crisis, minors, health, or finance:
- define a human escalation path,
- show local crisis/emergency resources,
- avoid automated diagnosis or advice,
- require privacy review before launch.

## References

- `~/.qoder/plugins/cache/local/gemi-skills/0.1.0/knowledge/app_opportunity_lab_playbook.md`
- `~/.qoder/plugins/cache/local/gemi-skills/0.1.0/knowledge/cross_platform_uiux_qa_security_playbook.md`
- `~/.qoder/plugins/cache/local/gemi-skills/0.1.0/knowledge/finance_economics_macro_micro_map.md`
- `~/.qoder/plugins/cache/local/gemi-skills/0.1.0/knowledge/psychology_mental_health_and_modern_problems.md`
