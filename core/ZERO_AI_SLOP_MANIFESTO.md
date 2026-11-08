# Human Technical Writing & Anti-AI UX Prose Protocol

> **Reference Context:** Distilled from Gemini Argon analysis, Google Developer Documentation Style Guide, Apple HIG, Microsoft Writing Style Guide, Mailchimp Voice & Tone, and humanization tools (`danobi/proselint`, `errata-ai/vale`, `spencergoldade/cursor-ux-writer`, `jpeggdev/humanize-writing`).

---

## 1. The Anatomy of AI Prose ("AI Slop" in Writing)

LLM writing is easily recognized by predictable statistical signatures: hyperbolic adjectives, false syntactic drama, structural over-organization, and sycophantic conversational habits.

| AI Writing Trait | Root Cause in LLM | Human Engineering Standard |
| :--- | :--- | :--- |
| **Banned Vocabulary Buzzwords** | High likelihood transitions to corporate superlatives. | Replace adjectives with concrete metrics and architectural facts. |
| **Negative Parallelisms** | *"It's not just X, it's Y"*. Overused rhetorical contrast device. | State what the system does directly in the affirmative. |
| **Em-Dash Addiction (—)** | Default syntactic separator for subordinate thoughts. | Use periods, commas, or parentheses. Vary sentence length naturally. |
| **Mechanical Bold-Colon Lists** | `**Feature:** Explanation...` repeated 5–10 times. | Use cohesive paragraphs, technical tables, or bullet points without bold headers when unnecessary. |
| **Emoji Inflation** | Emojis on every title and list item (🚀, ✨, 🛠️, 💡). | Omit decorative emojis completely from technical documentation, commit logs, and codebases. |
| **Sycophantic Conversational Openers** | *"Great question!"*, *"Certainly, let's explore!"*, *"Hope this helps!"*. | Speak as an objective Senior Peer Engineer: provide the answer or root cause in sentence 1. |

---

## 2. Banned Vocabulary & Construction Index

### 2.1. Banned AI-Tell Words
Unless describing an actual technical API or literal definition, **strictly avoid**:
- `delve`
- `tapestry`
- `seamless`
- `robust` (unless referring to strict fault-tolerance verification)
- `revolutionary`
- `game-changer`
- `blazingly fast`
- `testament`
- `crucial` (use specific impact instead)
- `groundbreaking`
- `beacon`
- `ethereal`, `celestial`, `radiant`, `kaleidoscopic`, `unyielding`, `ensnared` (Heretic statistical slop markers)

### 2.2. Banned Structural Habits
1. **Never use negative parallelism:**  
   - ❌ *"This application is not just a logging tool, but rather a comprehensive productivity ecosystem."*  
   - ✅ *"This application records transaction logs and synchronizes cache state to SQLite."*
2. **Never string together consecutive em-dashes:**  
   - ❌ *"The system is designed—through isolated architecture—to process data."*  
   - ✅ *"The system processes data using an isolated architecture."*
3. **Never start answers with sycophancy or filler:**  
   - ❌ *"Certainly! What a great question. Let's delve into how it works."*  
   - ✅ *"The root cause stems from a race condition in `SendKycOnboardingBrimoNS`."*

---

## 3. Essential Linters & Style Reference Guides

### 3.1. Repositories & Tools
- **`danobi/proselint`**: CLI linter for English prose; identifies redundant words, archaic corporate idioms, and hollow superlatives.
- **`errata-ai/vale`**: Extensible syntax-aware prose linter configured with styleguide rulesets (Google, Microsoft, Mailchimp).
- **`spencergoldade/cursor-ux-writer`**: Ruleset enforcing crisp microcopy, actionable error messages, and contextual empty states.
- **`jpeggdev/humanize-writing`**: 8-stage text refining process eliminating passive voice and rigid transitional connectors (*"Furthermore"*, *"Moreover"*, *"In conclusion"*).

### 3.2. Industry Standard Style Guides
- **`Wikipedia: Signs of AI Writing`**: Comprehensive catalog documenting AI vocabulary, syntactic ticks, and formatting artifacts.
- **`Google Developer Documentation Style Guide`**: Authoritative benchmark for technical READMEs, API references, and release notes: active voice, direct statements, objective tone, and zero promotional puffery.
- **`Mailchimp Content Style Guide`**: Voice & tone differentiation: warm and encouraging during onboarding and success; sober, unambiguous, and joke-free during data loss, billing failures, or system errors.
- **`Apple HIG — Writing` & `Microsoft Writing Style Guide`**: Interface capitalization (Title Case for native macOS menu bars vs Sentence case for buttons/dialogs), keyboard shortcut labels, and confirmation dialogs.

---

## 4. The 4 Operational Writing Contexts

```
┌────────────────────────────────────────────────────────┐
│             4 OPERATIONAL WRITING CONTEXTS             │
├──────────────────────────┬─────────────────────────────┤
│ 1. Technical Docs &      │ 2. In-App UX Microcopy      │
│    README.md             │    (Buttons, Errors, Empty) │
├──────────────────────────┼─────────────────────────────┤
│ 3. PR Reviews &          │ 4. Agent-to-Engineer        │
│    Architectural Diffs   │    Dialogue (IDE Chat)      │
└──────────────────────────┴─────────────────────────────┘
```

### Context 1: Technical Documentation & `README.md`
- **First Sentence Principle:** Sentence 1 must define the system's exact function, language/runtime, and core architectural pattern.
- **Code Grounding:** Every installation command, environment variable, or configuration flag must match exact entries in `package.json`, `Makefile`, or config manifests.
- **Format:** Use structured tables and diagrams over lengthy narrative descriptions.

### Context 2: In-App UX Microcopy (Buttons, Errors, Empty States)
- **Action-Verb Buttons:** Pair a specific transitive verb with its direct object:
  - ❌ *"Submit"*, *"OK"*, *"Continue"*, *"Yes"*
  - ✅ *"Save Changes"*, *"Delete Account"*, *"Export Report (CSV)"*, *"Cancel"*
  - Indonesian localized equivalents: *"Simpan Perubahan"*, *"Hapus Akun"*, *"Ekspor Laporan (CSV)"*, *"Batal"*
- **Actionable Error Messages:** Follow the mandatory two-part formula:
  $$\text{Error Message} = [\text{Factual Failure Description}] + [\text{Concrete Remediation Step}]$$
  - ❌ *"Error 422: Invalid input!"*
  - ✅ *"Failed to save configuration because port 4010 is already in use. Change the port value in `.env` and save again."*
- **Empty States:** One concise sentence explaining the feature's utility + exactly one Primary CTA button to create the first record.

### Context 3: Pull Request Descriptions & Code Reviews
- **Explain the "Why", Not the Diff:** The git diff already documents changed lines. The PR summary must explain:
  1. *Context & Problem Statement*
  2. *Architectural Decision & Trade-offs*
  3. *Verification & Edge-Case Test Scenarios*
- **Conventional Comments for Code Reviews:** Prefix review points with explicit severity labels:
  - `blocking:` Critical defect, race condition, data loss, or security violation that blocks merge.
  - `security:` Vulnerability, secret exposure, or sanitization gap.
  - `suggestion:` Concrete improvement with proposed code snippet.
  - `nit:` Minor formatting or naming convention adjustment.
  - `question:` Clarification regarding non-obvious business logic or edge case handling.

### Context 4: Agent-to-Engineer Dialogue (IDE Chat & Terminal)
- **Direct First Sentence:** Start with the exact technical diagnosis, file location, or executed change.
- **Peer Senior Engineer Persona:** Maintain an objective, collegial, and solution-focused tone. Challenge incorrect assumptions or flawed architectural ideas respectfully with evidence from the codebase.
- **Zero Filler Sign-Offs:** Omit closing pleasantries (*"Hope this helps! Feel free to ask more"*). End with logical next steps, open trade-offs, or verification status.

---

## 5. Platform-Specific UX Writing Nuances

| Platform | Primary Ergonomic Constraint | UX Writing Rules |
| :--- | :--- | :--- |
| **Desktop Applications** | Keyboard-first, rapid visual scanning | • Menu labels strictly 1–2 words.<br>• Never display long greeting banners (*"Welcome to your dashboard!"*).<br>• Tooltips must include keyboard shortcuts (e.g., `Search files (Ctrl+K)`). |
| **Web Applications** | Moderate canvas space, URL-addressable | • Section headers explain purpose in 1 sentence.<br>• Empty states provide clear orientation + 1 primary action.<br>• Breadcrumb trails match page titles verbatim. |
| **Mobile Applications** | Narrow screen width, truncation danger | • Bottom Tab Bar labels: **maximum 1 word**.<br>• App Bar headers: **maximum 2–3 words**.<br>• Use Bottom Sheets with short bullet items, not multi-paragraph modals.<br>• **Verbs:** Use *"Tap"* (Ketuk) or *"Swipe"* (Geser); **never use *"Click"*** on mobile touchscreens. |

---

## 6. Pre-Flight Writing Quality Audit
Before outputting documentation, UI copy, or PR reviews, verify:
- [ ] Are all banned words (`delve`, `tapestry`, `seamless`, `robust`, `revolutionary`, etc.) completely absent?
- [ ] Are negative parallelisms (*"not just X, but rather Y"*) eliminated?
- [ ] Are buttons labeled with specific action verbs (*"Save Changes"* vs *"Submit"*)?
- [ ] Do error messages state both what failed and how to resolve it?
- [ ] Are mobile verbs platform-accurate (*"Tap"* / *"Swipe"* instead of *"Click"*)?
- [ ] Is conversational filler stripped from the opening sentence?
