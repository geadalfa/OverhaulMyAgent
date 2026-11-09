# QODER.md - Qoder Desktop & CLI Harness Configuration

> **Harness:** [Qoder](https://qoder.com) (Desktop app + CLI agent)
> **Config root:** `~/.qoder/` (user scope) and `<project>/.qoder/` (project scope)
> **This repository is directly installable as a Qoder local plugin** — see `install/install_qoder.sh`.

---

## 1. Primary Guidelines

- **Persona:** Deterministic Senior Staff Engineer & AI Partner.
- **Tone:** Concise, direct, evidence-based. No sycophancy.
- **Language:** English for internal reasoning, rules, and documentation; user's language for dialogue.
- **Safety & Verification:** Run builds, tests, and linters and read the real output before reporting a task as completed.

## 2. Core Rules

1. Always inspect actual source code before calling functions or methods.
2. Use bounded reads (50–100 lines). Never read thousands of lines at once.
3. Enforce the 5 Quality Gates (Blast Radius, Architecture Isolation, Concurrency/Locks, Bottom-Up Execution, Adversarial Reflexion) — `core/FIVE_QUALITY_GATES.md`.
4. For progressive disclosure, read specialized modules listed in `core/ROUTER.md`.
5. Prefer dedicated tools (`Read`, `Edit`, `Grep`, `Glob`) over shell equivalents.

---

## 3. Qoder Layout Mapping

OverhaulMyAgent maps onto Qoder's native directory contract:

| OverhaulMyAgent | Qoder location (user scope) | Notes |
| :--- | :--- | :--- |
| `QODER.md` | `<project>/QODER.md` | Project instruction manifest; Qoder also honours root `AGENTS.md` |
| `skills/<name>/SKILL.md` | plugin `skills/` directory | Frontmatter `name` + `description`; invoked as `<plugin>:<skill>` |
| `knowledge/*.md` | plugin `knowledge/` | On-demand reference docs, never loaded at boot |
| `tools/*` | plugin `tools/` or `~/.qoder/sync/` | Deterministic scripts invoked via the Bash tool |
| `mcp/qoder_settings.template.json` | `~/.qoder/settings.json` → `mcpServers` | Merge, never blind-overwrite |
| `core/*.md` | plugin `references/` | Micro-kernel: boot payload only |

### 3.1 Plugin manifest

`.qoder-plugin/plugin.json` declares this repository as a Qoder plugin:

```json
{
  "name": "overhaul-my-agent",
  "displayName": "OverhaulMyAgent",
  "version": "1.0.0",
  "skills": "./skills/"
}
```

The registry entry lives in `~/.qoder/plugins/installed_plugins_v2.json`:

```json
{
  "version": 2,
  "plugins": {
    "overhaul-my-agent@local": [
      {
        "scope": "user",
        "installPath": "~/.qoder/plugins/cache/local/overhaul-my-agent/1.0.0",
        "version": "1.0.0",
        "displayName": "OverhaulMyAgent"
      }
    ]
  }
}
```

Enable it in `~/.qoder/settings.json`:

```json
{ "enabledPlugins": { "overhaul-my-agent@local": true } }
```

---

## 4. Qoder-Specific Constraints

These are hard-won invariants. Violating them silently breaks the harness.

1. **`settings.json` must be UTF-8 *without* a BOM.** Qoder's strict MCP config reader rejects a BOM-prefixed file with `SETTINGS_JSON_INVALID`, which silently disables **all** user MCP servers. Symptom: servers configured but never `ready`, and `[MCP] MCP config read failed` in the app `main.log`. If MCP stops loading, check the first bytes for `EF BB BF` and strip them.
2. **`disabledTools` is not part of the Qoder `mcpServers` schema.** Drop it when migrating from other harnesses; restrict tools in Extensions → Connectors instead.
3. **MCP servers are lazy-loaded.** They are not in the static tool list; discover and invoke them through `mcp_list` → `mcp_get` → `mcp_call` with the fully-qualified `mcp__<server>__<tool>` name. An empty `mcp_list` result does not mean the server is unconfigured.
4. **Restart Qoder after config writes.** Plugin skills and MCP servers are loaded at startup; editing `settings.json` or the plugin registry does not hot-reload.
5. **Preserve machine-specific keys when merging `settings.json`** (e.g. `qoder.computer-control.*`). Merge; never replace the whole file from a template.
6. **Never commit live credentials into `settings.json` backups.** Distribute `mcp/*.template.json` with `YOUR_*_HERE` placeholders only.

---

## 5. Memory Contract

Qoder persists file-based memory. OverhaulMyAgent uses it for durable engineering lessons, not for state that the repository already expresses.

- **User scope:** `~/.qoder/memory/` — true across every project.
- **Project scope:** `~/.qoder/projects/<project-slug>/memory/` — this project only.
- **Index:** `MEMORY.md` is a pointer list (`- [Title](file.md) — one-line hook`), never memory content. Keep it under 200 lines.
- **Entry format:** kebab-case filename plus frontmatter:

```markdown
---
name: short-kebab-slug
description: one-line summary specific enough to decide future relevance
metadata:
  type: user | feedback | project | reference
---

Body. For feedback/project types: rule first, then **Why:** and **How to apply:**
```

- **Routing:** `user` → always user scope; `project` → always project scope; `feedback` → user scope unless project-wide; `reference` → project scope unless the resource is org-wide.
- **Do not store** code patterns, architecture, file paths, git history, or fix recipes — those are derivable from the repository. Memory that names a file, flag, or function is a claim about the past: verify it still exists before recommending it.

---

## 6. Boot Payload (Progressive Disclosure)

Load at boot (~2,500 tokens): `core/CORE_SYSTEM_PROMPT.md` + `core/ROUTER.md`.
Everything else is read on demand:

| Intent | Read |
| :--- | :--- |
| Refactor / multi-file change | `skills/plan-first/SKILL.md` |
| Bug, crash, failing test | `skills/systematic-debugging/SKILL.md` |
| Spec-driven feature | `skills/spec-driven-development/SKILL.md` |
| UI / component styling | `skills/anti-slop-ui-design/SKILL.md` |
| Any third-party API call | `skills/no-invented-code/SKILL.md` |
| Before claiming "done" | `skills/verify-before-done/SKILL.md` |
| Financial math | `tools/financial_calculator.py` |
| Web extraction | `tools/fetch_web.py` |

---

## 7. Installation

```bash
# Global user-scope install (plugin + skills + knowledge + tools)
chmod +x install/install_qoder.sh
./install/install_qoder.sh

# Per-project install (QODER.md only)
python install/setup_harness.py --target qoder --dir /path/to/your/project
```

Windows users: `install\install_qoder.ps1`.

After installing, **restart Qoder** so the plugin and MCP servers load. Verify with
`mcp_list` and by checking that `overhaul-my-agent:*` skills appear in the skill listing.
