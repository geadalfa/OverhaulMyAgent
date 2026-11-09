# Qoder Harness Integration & Privacy Publishing Gate

Durable engineering knowledge for running this agent OS inside **Qoder**
(Desktop app + CLI) and for publishing a private agent install into a PUBLIC
repository without leaking personal or employer data.

---

## 1. Qoder configuration layout

| Purpose | Path |
| :--- | :--- |
| User config root | `~/.qoder/` |
| Settings + MCP servers | `~/.qoder/settings.json` |
| User memory | `~/.qoder/memory/` (+ `MEMORY.md` index) |
| Project memory | `~/.qoder/projects/<slug>/memory/` |
| Plugin registry | `~/.qoder/plugins/installed_plugins_v2.json` |
| Local plugin payload | `~/.qoder/plugins/cache/local/<name>/<version>/` |
| Standalone skills | `~/.qoder/skills/` |
| Logs | `~/.qoder/logs/` |

A local plugin needs `.qoder-plugin/plugin.json`:

```json
{ "name": "x", "displayName": "X", "version": "1.0.0",
  "description": "...", "author": { "name": "..." }, "skills": "./skills/" }
```

Registry entry shape (`<name>@local`), then enable it in settings:

```json
{ "version": 2, "plugins": { "x@local": [ { "scope": "user",
  "installPath": "/abs/path/.../x/1.0.0", "version": "1.0.0",
  "installedAt": "...", "lastUpdated": "...", "displayName": "X" } ] } }
```

```json
{ "enabledPlugins": { "x@local": true } }
```

## 2. Hard invariants (violating these fails silently)

1. **`settings.json` must be UTF-8 *without* a BOM.** A BOM makes Qoder reject
   the file with `SETTINGS_JSON_INVALID` and silently disables **every** user MCP
   server. Symptom: servers configured but never `ready`;
   `[MCP] MCP config read failed` in the app `main.log`. Check the first three
   bytes for `EF BB BF`.
2. **`disabledTools` is not in the Qoder `mcpServers` schema.** Drop it when
   migrating from other harnesses; restrict tools in Extensions → Connectors.
3. **MCP servers are lazy-loaded.** They are absent from the static tool list;
   discover and call them via `mcp_list` → `mcp_get` → `mcp_call` with the
   fully-qualified `mcp__<server>__<tool>` name. An empty `mcp_list` result does
   not mean the server is unconfigured.
4. **Restart Qoder after any config write.** Plugins, skills and MCP servers load
   at startup; editing `settings.json` or the registry does not hot-reload.
5. **Merge, never replace, `settings.json`.** Preserve machine-specific keys such
   as `qoder.computer-control.*`. Keep timestamped `.bak_*` copies.
6. MCP `command` should be resolvable on the target platform. Cross-platform
   migration needs `npx.cmd`↔`npx`, `uvx.exe`↔`uvx`, and absolute-path rewriting;
   Windows-only servers should be marked `"disabled": true` elsewhere.

## 3. Memory contract

- `MEMORY.md` is an **index of pointers**, never content: `- [Title](file.md) — hook`.
- Entry frontmatter: `name`, `description`, `metadata.type` ∈
  `user | feedback | project | reference`.
- Routing: `user` → user scope always; `project` → project scope always;
  `feedback` → user scope unless project-wide; `reference` → project scope unless
  the resource is org-wide. Writing a `project` entry into user scope is rejected.
- Do not store what the repository already expresses (code patterns, architecture,
  paths, git history, fix recipes). A memory naming a file or flag is a claim about
  the past — verify it still exists before recommending it.

---

## 4. Publishing a private install to a public repo

`tools/qoder_hub_sync.py` is the only sanctioned path. Design invariants:

1. **Memory is never published.** It holds personal preferences by definition.
2. **Existing items update; new items quarantine.** Anything not already tracked
   goes to quarantine unless `--allow-new` is passed. Auto-publishing brand-new
   files is how private material reaches a public repo.
3. **Denylists and frozen paths are never overwritten.** Some published documents
   are sanitised by hand because their local counterparts legitimately name
   internal systems.
4. **Redact before scanning, then scan the redacted text.** Home paths and the
   operator's name are rewritten (e.g. to `<HOME>`, `/Users/<user>`, `User`), and
   every redaction is reported. Anything still matching a block pattern is
   quarantined, never silently rewritten.
5. **Quarantine lives OUTSIDE the git working tree** (`~/.qoder/quarantine/<repo>`).
   Rejected material can contain real credentials; inside the tree a careless
   `git add -A` would stage it.
6. **Whole-repository scan before commit.** One finding aborts; nothing is pushed.
7. **Sensitive identifiers are stored base64-encoded inside the tool**, because the
   repository's own CI linter rejects those literals in any tracked file.

### Leak vectors actually observed (all real, all initially missed)

| Vector | Why naive scanning missed it | Countermeasure |
| :--- | :--- | :--- |
| Credential passed as a **CLI argument** (`--some-token <value>`) instead of `env` | Redaction only covered `env` values | Redact the value following any secret-looking flag; token-shaped arg detection; final safety net over every string in the generated config |
| **Commit metadata**: author name + corporate e-mail | Content scanners read blobs, not commit objects | Rewrite with a mailmap; enforce a private repo-local identity; refuse to commit when `user.email` looks corporate/intranet |
| Employer **system/vendor/squad names** as bare words | Regex looked for domains, tokens, IPs | Explicit terminology blocklist |
| Personal **hardware specs** | Not a secret shape | Terminology blocklist mirrored from the CI linter |
| **Cloud-storage account path** containing a personal e-mail | Path looked like ordinary config | Dedicated pattern + redaction |
| Absolute **home paths** (`/Users/<name>`, `C:\Users\<name>`) | Read as harmless detail | Redaction rules, reported per file |

### False positives worth designing around

- DOI suffixes (`10.1177/1745691615623247`) match a 16-digit national-ID pattern →
  exclude when preceded by `/`, `.`, `_`, `-`.
- Prose that *mentions* `id_rsa` as advice ("never commit `id_rsa`") matches an SSH
  key pattern → require an actual path shape (`.ssh/id_*`).
- npm specifiers (`pkg@1.2.3`) match a naïve e-mail regex → require an alphabetic
  TLD.
- Base64 data URIs in JSON schemas match a "base64 credential" pattern → do not
  apply that heuristic to prose; apply it only to structured config values.

A blocked file is a *review* signal, not an error: the already-sanitised published
version stays untouched.

---

## 5. macOS automation: launchd, TCC and throttling

Three lessons learned the hard way while wiring always-on sync agents.

1. **Throttle by waiting, never by dropping.** `WatchPaths` fires only on change.
   A job that exits early because it is inside the throttle window loses that event
   forever — the change is not backed up until something else changes. Correct
   shape: acquire a lock (so bursts collapse into one run), then *sleep* the
   remaining window, then do the work.
2. **launchd cannot write to `~/Library/CloudStorage` without Full Disk Access.**
   The same script succeeds from an app shell (inheriting that app's TCC grant) and
   fails under launchd with `Operation not permitted`. Writability probes are
   unreliable here: `touch` succeeded while `cp` was denied. Robust pattern: build
   the output in **local staging**, then copy to the cloud folder with retries and
   post-copy verification; on failure keep staging and log the exact remediation
   (System Settings → Privacy & Security → Full Disk Access → add `/bin/bash`).
3. **A stale credential in the macOS keychain silently wins.** With an
   `internet-password` entry for the host under a *different* account, pushes fail
   with 403 as that account. Fix: reset the helper chain before supplying your own —
   `git -c credential.helper= -c credential.helper='!f() { ...; }; f' push ...`.
   Pass the secret through the environment, never through argv or the remote URL,
   and never persist it in `.git/config`.

Also: `git filter-repo` removes the `origin` remote after rewriting — re-add it,
`fetch`, then push with `--force-with-lease`. Verify the rewrite by scanning
**every blob in every commit**, not just the working tree, and remember that
force-pushing a public repo does not recall forks, clones or caches.

---

## 6. Pre-publication checklist

1. Scan working tree **and** full history (all blobs, all commits).
2. Scan **commit metadata** (author/committer name and e-mail), not just content.
3. Mirror the repository's own CI linter patterns locally before pushing.
4. Confirm no credential appears in `env`, in CLI args, or in file names.
5. Confirm the quarantine directory is gitignored **and** outside the tree.
6. Create a restorable backup (`git bundle create … --all`) before rewriting history.
7. After pushing, confirm CI is green and that published files resolve over raw HTTP.
8. If a secret was ever transmitted, **rotate it** — a rejected push still exposed it.
