# Knowledge Ingestion Automation — Trigger Rule

**Status:** active · built 2026-11-10 · companion skill: `~/.qoder/skills/knowledge-ingestion/SKILL.md`

## Trigger phrases

When User says any of the following, run the `knowledge-ingestion` workflow — do not stop at a chat summary:

- "tolong pelajari …"
- "simpan ke knowledge"
- "pelajari dan simpan"
- "masukkan ke knowledge"
- "update pengetahuan …"
- "ingat ini / catat ini"
- "pelajari repo/link/dokumen ini"

## Required behavior

1. Verify the primary source; record author, license, version, date.
2. Extract the durable core: what it is, why it matters, concepts, workflow, verified behavior, limitations, ethics.
3. Choose the **smallest useful set** of durable assets:
   - knowledge doc (default for facts/domain material),
   - skill (repeatable decision workflow),
   - tool/script (deterministic computation or automation),
   - memory (user preference, feedback rule, project fact, reference pointer),
   - MCP config/server (only when new external access is necessary and consented),
   - plugin (only when packaging multiple capabilities).
4. Deduplicate against existing knowledge and memory indexes.
5. Write, cross-link, and update indexes.
6. Verify files, scripts, and references.
7. Report what was learned, what was saved where, what was not saved and why, and the caveats.

## Routing matrix

| Signal | Destination |
|---|---|
| Source explains a domain, tool, standard, or concept | Knowledge doc |
| Source implies a repeatable process Gemi must follow | Skill |
| Source requires exact calculation or automation | Tested script under the skill or `~/.qoder/tools/` |
| Source changes how Gemi collaborates with User | Memory type `user` or `feedback` |
| Source is a project-specific decision | Project memory |
| Source is a pointer User will revisit | Memory type `reference` |
| Source requires a new external service | MCP server config, with consent and credentials |
| Multiple skills/tools should ship together | Qoder plugin |

## Non-negotiables

- No fabrication; every claim traceable to the source.
- No secrets, tokens, credentials, or PII in knowledge or memory.
- Respect licenses; summarize, do not reproduce large copyrighted text.
- Do not execute untrusted code without a reason; delete temp clones.
- Record limitations and version/date; do not present marketing claims as verified fact.
- For finance/psychology/security topics, apply the existing domain ethics.

## Example

User: "Tolong pelajari https://github.com/apissaj/humanizer-id dan simpan ke knowledge."

Result:
- Knowledge doc `humanizer_id_indonesian_academic_editing.md` (repo analysis, 420 rules, CLI, verified limitations).
- Skill `knowledge-ingestion` (this automation).
- Reference memory (when auto-memory is enabled).
- No new MCP server or tool needed; the existing repo scanner covered repository analysis.
