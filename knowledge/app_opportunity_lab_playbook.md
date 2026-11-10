# App Opportunity Lab — From Problem to Validated App

Method for turning a real problem (finance, psychology, productivity, daily life) into a desktop, web, or mobile app without hype, harm, or wasted build time.

---

## 1. Principles

1. **Problem first, technology last.** No app until the problem is observed, not imagined.
2. **Smallest evidence-based intervention.** Prefer a narrow tool that works over a broad platform that impresses.
3. **Ethics are a feature.** Privacy, consent, crisis escalation, and honest claims are part of the architecture.
4. **Local-first by default.** Sensitive data stays on-device unless sync is necessary.
5. **Deterministic math, sourced facts.** Financial numbers come from code and cited data, never model guesses.
6. **Build to learn.** Validate with prototypes and real users before polishing.

## 2. Workflow (Double Diamond)

### Discover

1. **Collect raw problems** from interviews, observation, support tickets, communities, and your own life.
2. **Interview for past behavior**, not hypothetical intent:
   - "Tell me about the last time this happened."
   - "What did you do next?"
   - "What did it cost you — time, money, stress?"
3. **Map the current workaround**: spreadsheet, notes, WhatsApp, nothing.
4. **Quantify**: frequency, severity, willingness to pay, existing spend.

### Define

5. **Write the job-to-be-done**: "When [situation], I want to [motivation], so I can [outcome]."
6. **Choose the user segment** narrow enough to serve well.
7. **Run domain gates** (below).
8. **Define success metrics** before building: activation, task success, retention, outcome.

### Develop

9. **Prototype the smallest flow** (Figma or clickable HTML); test with 5 users.
10. **Choose the platform** with the matrix below.
11. **Design architecture**: local-first, sync, integrations, data retention.
12. **Plan QA and security**: test pyramid, threat model, release gate.

### Deliver

13. **Build MVP** with one core loop.
14. **Beta with real users**, measure, iterate.
15. **Decide**: double down, pivot, or stop.

## 3. Platform selection

| Need | Desktop (Windows/macOS) | Web | Native mobile |
|---|---|---|---|
| Heavy local processing / files | Best | Weak | Weak |
| Privacy / offline | Best | Medium | Medium |
| Broad reach / no install | Weak | Best | Medium |
| Daily quick capture | Medium | Medium | Best |
| Hardware / OS integration | Best | Weak | Medium |
| Real-time collaboration | Medium | Best | Good |
| App-store distribution | Medium | N/A | Best |

Hybrid is valid: desktop engine + local web UI (the pattern used by DiagnoseMyDisk and ConvertMyDocuments), or mobile capture + web dashboard.

## 4. Domain gates

### Finance gate

- No personalized investment advice without licensing.
- No custody, lending, or payments without OJK/BI permissions.
- Disclose assumptions, fees, taxes, and data dates.
- Deterministic calculations; show nominal and real values.
- Never invent rates or returns.

### Psychology gate

- No diagnosis, prescription, or claim to replace a professional.
- Screening tools are labeled as screening aids.
- Crisis escalation path with local resources.
- Consent, encryption, export, deletion; protect minors.
- Evidence-based content with citations; human oversight for high-risk signals.

### Security and privacy gate

- Threat model before code.
- AuthZ on every endpoint; least privilege.
- Encrypt sensitive data at rest and in transit.
- No secrets in logs or client bundles.
- Test authorization, update integrity, and install/rollback.

### Legal gate (Indonesia)

- UU PDP for personal data.
- UU ITE for unauthorized access.
- OJK/BI licensing for financial services.
- Consumer protection for subscriptions and refunds.

## 5. Validation methods

| Method | Question answered | Cost |
|---|---|---|
| Problem interview | Is this real and frequent? | Low |
| Workaround audit | What do they use today? | Low |
| Clickable prototype | Can they complete the flow? | Medium |
| Concierge MVP | Would they use a manual version? | Medium |
| Landing-page smoke test | Is there demand? | Low |
| Beta cohort | Does it retain? | High |

## 6. Opportunity scorecard

Score each 1–5:

| Dimension | Weight | Question |
|---|---:|---|
| Severity | 25% | How painful is the problem? |
| Frequency | 20% | How often does it occur? |
| Willingness to pay | 15% | Is there existing spend or budget? |
| Feasibility | 20% | Can it be built and maintained solo? |
| Differentiation | 10% | Why this app, not the incumbents? |
| Safety/ethics fit | 10% | Can harm be controlled? |

**Score = weighted sum − risk penalty (0–2).** Build only if ≥ 3.8 and no red gate is violated.

## 7. Templates

### Concept one-pager

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
```

### Interview guide

1. Tell me about the last time this problem happened.
2. What triggered it?
3. What did you try first? Then what?
4. What did it cost you?
5. What would "solved" look like?
6. Who else is involved?
7. What have you paid for before?

### Validation scorecard

| Signal | Weak | Strong |
|---|---|---|
| Users describe the problem unprompted | 0–2 | 5+ |
| Existing workaround costs money/time | None | Paid tool or hours/week |
| Prototype task success | <50% | >80% |
| Beta retention (week 4) | <10% | >30% |
| Willingness to pay | "Maybe" | Pre-order / paid pilot |

## 8. Anti-patterns

- Building a platform before a single workflow works.
- Adding AI to a problem that needs math or a checklist.
- Copying a paid app feature-for-feature without a differentiated user.
- Ignoring crisis escalation in a mental-health product.
- Collecting health/financial data "for later."
- Measuring downloads instead of outcomes.
- Polishing UI before validating the problem.

## 9. Integration

- Repo learning: `repo-architecture-mentor`
- Architecture decisions: `architecture` skill (ADR)
- Codebase research: `researching-codebase`
- UI/UX and QA/security: `cross_platform_uiux_qa_security_playbook.md`
- Finance domain: `finance_economics_macro_micro_map.md`
- Psychology domain: `psychology_mental_health_and_modern_problems.md`
