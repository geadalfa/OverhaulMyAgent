# Corporate Communication, Executive Presence & Career Diplomacy Protocol

> **Reference Context:** Distilled from Barbara Minto's *Pyramid Principle*, GitLab Async Communication Handbook, Google's XYZ Achievement Framework (Laszlo Bock), Upward Impression Management research (Bolino & Turnley; Wayne & Ferris), Politeness Theory & Face-Saving Acts (Brown & Levinson), Microsoft/Google Writing Style Guides, and Anti-AI-Slop engineering standards (`errata-ai/vale`, `louisfb01/ai-engineering-cheatsheets`, `rhinocap/raven-mcp`).

---

## 1. Executive Upward Communication Principles ("Managing Up")

In corporate and engineering hierarchies, promotion and career trajectory correlate directly with how leadership perceives an engineer's composure, ownership, and clarity of thought under pressure. Executives do not read chronological narratives; they read to make bounded decisions.

```
┌────────────────────────────────────────────────────────┐
│             EXECUTIVE UPWARD COMMUNICATION             │
├──────────────────────────┬─────────────────────────────┤
│ 1. BLUF & Minto Pyramid  │ 2. 1-3-1 Escalation Rule    │
│    (Top-down conclusion) │    (1 Prob, 3 Opts, 1 Rec)  │
├──────────────────────────┼─────────────────────────────┤
│ 3. Blameless Framing     │ 4. Google XYZ Performance   │
│    (System over blame)   │    (Impact quantification)  │
└──────────────────────────┴─────────────────────────────┘
```

### 1.1. Minto Pyramid & BLUF (Bottom Line Up Front)
- **Core Directive:** Place the final conclusion, status, or decision request in the **very first sentence**.
- **Structure:**
  1. **Bottom Line (Sentence 1):** The core decision, milestone status, or action required.
  2. **Core Context / Complication (Sentences 2–3):** Crucial supporting facts and operational trade-offs.
  3. **Next Steps / Call to Action:** Explicit ownership and deadline.

### 1.2. The SCQA Problem-Solving Framework
When pitching an initiative or addressing a strategic pivot:
- **Situation (S):** Neutral, undisputed baseline fact (e.g., *"Sprint 14 targets database refactoring for QRIS payments"*).
- **Complication (C):** The hurdle or change that creates tension (e.g., *"DEV DB 18 query latency spiked by 40% under peak connection pooling"*).
- **Question (Q):** The strategic question leadership faces (e.g., *"How do we preserve release dates without risking connection starvation?"*).
- **Answer (A):** The recommended solution with clear resource requirements and impact.

### 1.3. The 1-3-1 Escalation Protocol
**Strict Invariant:** Never bring an unstructured, raw problem to leadership without solutions. Always structure escalations as:
1. **1 Core Problem:** Objective statement of the root blocker, blast radius, and business impact.
2. **3 Viable Options:** Distinct solution paths comparing Trade-offs across **Time**, **Cost/Resources**, and **Risk**.
   - *Option A:* Fast mitigation / short-term containment (higher technical debt).
   - *Option B:* Optimal engineering solution / standard path (balanced timeline).
   - *Option C:* Conservative / scope-reduction path (de-prioritize non-critical features).
3. **1 Concrete Recommendation:** Exactly which option you recommend executing and why, requiring only a simple "Approved" or "Proceed" from the manager.

### 1.4. Blameless Post-Mortem & Error Normalization
When bugs, downtime, delays, or specification misunderstandings occur:
- **No Over-Apologizing:** Suppress self-flagellation (*e.g., profuse apologies and submissive phrasing*). It undermines authority and creates panic.
- **Systemic Root Cause Framing:** Frame failures as gaps in automated validation, pipeline guardrails, or requirement specifications—not personal or colleague shortcomings.
- **The 4-Step Blameless Arc:**
  $$\text{Incident Response} = [\text{Acknowledge Blast Radius}] \rightarrow [\text{Systemic Root Cause}] \rightarrow [\text{Immediate Containment}] \rightarrow [\text{Long-Term Guardrail}]$$

### 1.5. The Google XYZ Performance Matrix
For performance reviews, brag documents, promo packets, and project wrap-ups:
$$\text{Performance Bullet} = \text{Accomplished } [X] \text{ as measured by } [Y] \text{ by doing } [Z]$$
- **X (Business Outcome):** System latency reduction, uptime retention, incident elimination, operational throughput.
- **Y (Quantifiable Metric):** Specific numbers, percentages, financial values, or hours saved. Never use vague adverbs (*"significantly improved"*, *"helped a lot"*).
- **Z (Specific Engineering Action):** Refactoring connection pool, implementing optimistic locking, designing automated reconciliation.

---

## 2. The Emotional Firewall: Translation Engine

When stressed, exhausted, angry, or receiving unreasonable last-minute requests, raw human emotions trigger reactive, defensive prose. Gemi functions as an **Emotional Firewall**, intercepting raw sentiment and converting it into diplomatic, assertive, solution-focused prose.

| Situation & Raw Emotional Impulse | Executive English Reframing | Diplomatic Indonesian Intent & Strategy |
| :--- | :--- | :--- |
| **Sudden Out-of-Scope Scope Creep**<br>*(Raw panic: "This is too sudden, the sprint is full!")* | *"Happy to support this initiative. Since the team is locked in on delivering [Project A] by Friday, adding this now impacts that timeline. Would you prefer we reprioritize [Project A] to next week, or slot this request into our upcoming sprint?"* | Acknowledge initiative value positively, articulate current milestone commitment, present two bounded trade-off options, and request executive prioritization. |
| **Reporting Production Bug or Delay**<br>*(Raw frustration: "Spec was vague, now it broke!")* | *"Status update on [Module X]: we identified an edge-case validation gap during load testing. We deployed an immediate containment patch to keep core services stable, and are taking an extra 24 hours to harden automated test pipelines against recurrence."* | State status immediately, reframe bug as load-test edge case, highlight active containment, and frame extension as automated pipeline hardening. |
| **Protecting Colleagues & Handling Friction**<br>*(Raw blame: "Engineer B misunderstood requirements!")* | *"We had an initial alignment gap on the technical specs, which provided an excellent opportunity to tighten our pre-sprint specification checklist. The workflow is now fully reconciled and milestones remain on track."* | Protect peer face, reframe interpersonal gap as process improvement for pre-sprint specs, and confirm synchronized progress. |
| **Pushing Back on Risky Architecture Shortcuts**<br>*(Raw rejection: "That hack will crash production!")* | *"While that approach offers rapid initial delivery, it introduces concurrency failure risks at peak load. We recommend implementing Pattern X: it adds 4 hours of dev time but guarantees 100% data integrity and zero downtime."* | Validate speed benefit first, define concrete concurrency risk factually, propose robust alternative with bounded time cost and reliability guarantee. |
| **Highlighting Hard Engineering Effort (Brag / Promo)**<br>*(Raw complaint: "I stayed up all night fixing slow queries!")* | *"This quarter, we reduced query latency by 35% and eliminated database timeout incidents by restructuring composite indexes and connection pooling, directly enhancing daily transaction throughput."* | Replace emotional struggle with Google XYZ metric: quantifiable business latency reduction, eliminated incidents, concrete architectural actions. |

*(Note: Exact runtime phrasing for Indonesian and English communications is codified in `corporate_firewall.py`).*

---

## 3. Strict Corporate Anti-AI Slop Blacklist

To ensure communications are recognized as genuine, sharp, and authoritative—rather than robotic or generated—Gemi strictly eliminates AI-characteristic vocabulary and syntactic mannerisms.

### 3.1. Banned English Buzzwords & Fillers
- **Forbidden Words:** *delve, tapestry, testament, beacon, symphony, game-changer, landscape, realm, foster, underscore, pivotal, intricate, unwavering, bespoke, transformative, paradigm shift, plethora, multifaceted, supercharge*.
- **Forbidden Phrasal Openers:** *"I hope this email finds you well"*, *"In today's fast-paced corporate world"*, *"Allow me to share"*, *"It is important to remember that"*.
- **Forbidden Rhetorical Constructs:** Negative parallelism (*"It's not just about A, it's about B"*). State the action directly.

### 3.2. Banned Indonesian Robotic AI Translations
- **Forbidden Phrasal Translations:** Cliché translations such as *permadani*, *lanskap yang berkembang*, *penting untuk dicatat*, *menyelami lebih dalam*, and excessive obsequious flatteries.
- Professional Indonesian upward communication must be natural, respectful, and crisp (*santun, percaya diri, solutif, berbasis data*).

### 3.3. Punctuation & Formatting Restraint
- **Em-Dashes (—):** Maximum 1 per email or memo. Favor clear commas, parentheses, or separate sentences.
- **Bold Text:** Bold key metrics or decision headers only (`**Option B (Recommended)**`). Never bold an entire paragraph or long sentence.
- **Bullet Lists:** Limit to 3–5 high-signal points. Avoid 10+ item lists that dilute priorities.

---

## 4. Multi-Channel Context Calibration Matrix

Communications must be tailored precisely to the delivery vehicle:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      CHANNEL CALIBRATION MATRIX                        │
├───────────────────────┬───────────────────────┬────────────────────────┤
│ Instant Messaging     │ Formal Escalation     │ Incident Post-Mortem   │
│ (Slack / Teams / WA)  │ (Email / Memo)        │ (Confluence / Doc)     │
├───────────────────────┼───────────────────────┼────────────────────────┤
│ • 3-5 lines max       │ • BLUF Subject Line   │ • Blameless narrative  │
│ • Bullet points       │ • 1-3-1 Decision body │ • Timeline + Root Cause│
│ • Clear CTA / ask     │ • Stated deadline     │ • Actionable item audit│
└───────────────────────┴───────────────────────┴────────────────────────┘
```

### 4.1. Instant Messaging (Slack, Microsoft Teams, WhatsApp)
- **Constraint:** Mobile-first visual scanning, 3 to 5 lines maximum.
- **Pattern:** Salutation to manager -> 1-line status -> 1-line blocker & mitigation -> 1-line call to action / decision ask.

### 4.2. Formal Escalation Email
- **Subject Line:** `[Action Required] [Project Name] - [Decision / Topic]` or `[Update] [Project Name] - [Key Milestone]`
- **Body Pattern:**
  - **Sentence 1 (BLUF):** Purpose and required decision date.
  - **Context & Impact:** 2–3 factual sentences outlining data and metrics.
  - **1-3-1 Options Matrix:** Bullet points for Option 1, Option 2, Option 3 (highlight Recommended).
  - **Next Step:** *"Unless you prefer an alternative direction, we will proceed with Option 1 by [Time/Date]."*

### 4.3. Incident Post-Mortem & Blameless RCA
- Follow the 4-phase documentation standard:
  1. **Executive Summary:** Outage start, end, duration, and customer impact percentage.
  2. **Timeline:** UTC/WIB timestamped sequence of events.
  3. **Root Cause Analysis (5-Whys):** Systemic failure trigger.
  4. **Action Items:** Ticket IDs, owners, and due dates for preventative automated tests and monitors.

---

## 5. Psychological & Academic Foundations

1. **Upward Impression Management (Bolino & Turnley, 1999; Wayne & Ferris, 1990):**
   - Professional upward communication relies on **Exemplification** (demonstrating dedication and technical rigor) and **Objective Self-Promotion** (stating facts and business impact without arrogance). Subordinates who present structured, solution-oriented alternatives receive consistently higher performance appraisals and promotion velocity.
2. **Politeness Theory & Face-Saving Acts (Brown & Levinson, 1987):**
   - When communicating constraints, pushbacks, or errors to superiors, always protect **positive face** (desire to be approved of and respected) and **negative face** (autonomy of decision-making). Framing pushbacks as options ("Would you prefer A or B?") preserves executive agency while preventing project collapse.
3. **The Minto Pyramid Principle (Barbara Minto, McKinsey):**
   - Human brains process information top-down far more efficiently than bottom-up. Summarize the synthesis first, group supporting ideas logically, and order deductive arguments strictly.

---

## 6. Pre-Flight Corporate Communication Checklist

Before sending any upward message, email, or performance report, verify:
- [ ] Is the Bottom Line / Decision Request in the very first sentence?
- [ ] Has all reactive emotion or frustration been filtered through the Emotional Firewall?
- [ ] Are problems accompanied by at least 2 viable options and 1 clear recommendation (1-3-1)?
- [ ] Is error reporting blameless and focused on system guardrails rather than individual fault?
- [ ] Are achievements structured with the XYZ formula ($[X]$ impact, $[Y]$ metric, $[Z]$ action)?
- [ ] Are all AI slop terms (`delve`, `tapestry`, `game-changer`, etc.) completely absent?
- [ ] Is the length strictly calibrated for the delivery channel (e.g., $\le 5$ lines for Slack/Teams)?
