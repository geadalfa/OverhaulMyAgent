---
name: knowledge-ingestion
description: Use when User says "tolong pelajari", "simpan ke knowledge", "pelajari dan simpan", "masukkan ke knowledge", "update pengetahuan", or asks Gemi to remember a source. Ingests a repository, URL, document, or concept into the right durable assets — knowledge, skill, tool, MCP config/server, plugin, or memory — with source verification, deduplication, cross-linking, and a change report.
---

# Knowledge Ingestion

Turn a source into durable, reusable intelligence — not just a chat summary.

## Trigger phrases

Activate when User says any of:
- "tolong pelajari …"
- "simpan ke knowledge"
- "pelajari dan simpan"
- "masukkan ke knowledge"
- "update pengetahuan …"
- "ingat ini / catat ini"
- "pelajari repo/link/dokumen ini"

Do not ask "mau disimpan ke mana?" by default. Decide the smallest useful set of assets, do it, and report what changed. Ask only when the source is confidential, requires credentials, or the storage choice has a real trade-off.

## Non-negotiables

1. **Primary source first** — read the source itself; secondary summaries only for context.
2. **No fabrication** — every claim must be traceable to the source or a cited reference.
3. **No secrets/PII** — never store tokens, credentials, private keys, or personal data in knowledge/memory.
4. **Respect licenses** — summarize and cite; do not reproduce large copyrighted text.
5. **Deduplicate** — read existing knowledge and memory indexes before writing.
6. **Smallest useful set** — do not dump the same content into every category.
7. **Verify before claiming done** — files exist, indexes updated, scripts tested.
8. **Record limitations** — version, date, scope, conflicts, and what the source does not prove.

## Step 0 — Frame

Restate in one line what is being learned and why it matters to User. Classify the source:

| Source type | Examples |
|---|---|
| Repository | GitHub/Bitbucket repo, package, CLI, agent skill |
| Web/doc | Official docs, article, blog, standard/spec |
| Paper/book | Journal article, textbook, report |
| Concept | Method, framework, mental model |
| Internal | Company doc, Confluence page, runbook |

## Step 1 — Verify the source

Collect and record:
- canonical URL, author/publisher, license;
- version and last-updated date;
- scope and intended audience;
- evidence of quality (tests, CI, citations, stars are signals, not proof);
- known limitations or conflicts.

For repositories: fetch metadata, README, license, manifest, entry points, tests, and changelog. Clone shallow to a temp directory only when needed; never execute untrusted code without a reason; delete the temp clone afterward.

## Step 2 — Extract the durable core

Write down:
1. What it is and what problem it solves.
2. Key concepts and vocabulary.
3. Workflow or architecture.
4. Verified behavior (what you actually ran/read).
5. Limitations and failure modes.
6. Ethical/legal constraints.
7. How Gemi should apply it.

## Step 3 — Route to the right assets

| Need | Destination | When |
|---|---|---|
| Factual/domain knowledge | Knowledge doc in `gemi-skills` plugin + `~/.gemini/knowledge/` | Default for reference material |
| Repeatable decision workflow | Skill at `~/.qoder/skills/<name>/SKILL.md` | When the source implies a process to follow |
| Deterministic computation/automation | Script under the skill's `scripts/` or `~/.qoder/tools/` | When the work must be exact or repeatable |
| Durable user preference/rule | `~/.qoder/memory/` type `user` or `feedback` | When it changes future collaboration |
| Project fact/decision | Project memory | When it is true only for this project/workspace |
| Pointer to an external resource | `~/.qoder/memory/` type `reference` | When User will return to the source |
| New external service/API access | MCP server config | Only when the capability is necessary, credentials exist, and User consents |
| Package of multiple capabilities | Qoder plugin | Only when reusability/distribution justifies packaging |

Rules:
- One source may produce a knowledge doc **and** a skill **and** a memory pointer, but only if each adds distinct value.
- Do not add an MCP server just because it exists; document the existing capability if it already covers the need.
- Do not modify a synced plugin cache directly when a standalone skill is the durable home; prefer `~/.qoder/skills` for Qoder-specific workflows.
- Copy knowledge docs to `~/.gemini/knowledge/` when they should survive the cross-device sync.

## Step 4 — Deduplicate

1. Read `~/.qoder/memory/MEMORY.md` and the project memory index.
2. List the target knowledge directory and search for the same topic.
3. If an existing doc covers it, update that doc instead of creating a near-duplicate.
4. If the new source conflicts with an old one, record both, mark which is newer, and update the stale doc explicitly.

## Step 5 — Write

### Knowledge doc template

```markdown
# <Title>
Source · author · license · version · verified date
## What it is
## Why it matters
## Key concepts
## Workflow / architecture
## Verified behavior
## Limitations
## How Gemi should use it
## References
```

### Memory template

```markdown
---
name: <kebab-case>
description: <one line, specific>
metadata:
  type: user | feedback | project | reference
---

<fact/rule>
**Why:** …
**How to apply:** …
```

### Skill template

```markdown
---
name: <kebab-case>
description: Use when <trigger conditions>. <What it produces.>
---

# <Title>
## When to activate
## Non-negotiables
## Workflow
## Outputs
## References
```

## Step 6 — Cross-link and index

- Link related memory files with `[[name]]`.
- Add a one-line pointer to the correct `MEMORY.md` index.
- Reference the new knowledge doc from the relevant skill or memory.
- Update any existing doc that now contradicts the new one.

## Step 7 — Verify

- Files exist at the expected paths.
- Frontmatter is valid; no duplicate names.
- Scripts compile or run on a safe sample.
- `MEMORY.md` entries point to existing files.
- No secrets or PII in the content.
- If the source was a repo, remove the temp clone.

## Step 8 — Report

Report in Bahasa Indonesia:
1. What was learned (3–6 bullets).
2. What was saved, with paths (knowledge, skill, tool, memory).
3. What was intentionally **not** saved and why (e.g., no new MCP needed).
4. Verification evidence.
5. Caveats/limitations.

## Source-type playbooks

### Repository

1. Metadata: owner, description, license, version, last update.
2. Read README, manifest, entry points, tests, CI.
3. Run `repo_recon.py` for a map.
4. Run only safe demos; never install/execute untrusted code without a reason.
5. Extract architecture, rule/data assets, limitations.
6. Delete the temp clone.

### Web / official docs

1. Prefer the official source over blogs.
2. Record retrieval date and version.
3. Verify claims across at least two primary pages when possible.
4. Note paywalls/403s as access limitations, not as invalid sources.

### Paper / book

1. Record citation, DOI, edition, and page references.
2. Summarize findings; never reproduce long excerpts.
3. Distinguish the author's claim from the evidence.

### Internal / company doc

1. Check confidentiality before storing.
2. Redact names, credentials, customer data.
3. Store only what is needed for the task.

## Safety and ethics

- Stop if the source asks for credentials or invites running unknown binaries.
- Do not store medical, financial, or personal data about identifiable people.
- Do not present a source's marketing claim as verified fact.
- Do not use knowledge to enable harm, unauthorized access, or deception.
- For finance/psychology topics, keep the existing domain ethics: no advice/diagnosis, cite evidence, escalate high-risk cases.

## References

- Existing knowledge: `~/.qoder/plugins/cache/local/gemi-skills/0.1.0/knowledge/`
- Memory index: `~/.qoder/memory/MEMORY.md`
- Project memory index: `~/.qoder/projects/<project>/memory/MEMORY.md`
- Repo scanner: `~/.qoder/skills/repo-architecture-mentor/scripts/repo_recon.py`
