---
name: privacy-publish-gate
description: Use before publishing, syncing, or pushing any private agent asset (skills, knowledge, tools, MCP config, plugin payload, memory) to a PUBLIC repository, and whenever asked to "make sure my personal data does not leak". Runs the sanitising gate, audits working tree AND full git history AND commit metadata, and refuses to push on any finding.
---

# Privacy Publishing Gate

Publishing a private agent install into a public repository is how personal and
employer data leaks. This skill is the mandatory pre-flight.

## When to use

- Any push of skills / knowledge / tools / MCP config / plugin payload to a public repo.
- "Make sure my personal data isn't public", "sanitize this repo", "check for leaks".
- After adding a new sync or publishing automation.
- Before enabling any *automatic* push.

## Non-negotiable rules

1. **Never publish memory.** It holds personal preferences by definition.
2. **Never hand-copy** assets from a private install into a public repo. Use the
   gated publisher (`tools/qoder_hub_sync.py`).
3. **New items quarantine; only tracked items auto-update.** Auto-publishing
   unreviewed new files is the main leak path.
4. **Redact, then scan the redacted text.** Never publish a file that only
   *looks* clean because a secret was string-replaced.
5. **Quarantine stays outside the git working tree.**
6. **No push if the whole-repository scan has even one finding.**

## Audit procedure

Run all four. Passing only the first is how leaks survive.

1. **Working tree** — scan every tracked file for credentials, corporate/intranet
   hosts, private IPs, home paths, personal e-mail, internal system names,
   hardware identifiers.
2. **Full history** — scan every blob in every commit, not just HEAD. Prior
   commits keep the original text after a single sanitising edit.
3. **Commit metadata** — author/committer name and e-mail. A corporate address
   here is published permanently and content scanners never look at it.
4. **CI mirror** — run the repository's own linter patterns locally first; a push
   that fails CI after a history rewrite wastes a force-push.

## Leak vectors that are easy to miss

- Credential passed as a **CLI argument** (`--x-token <value>`) instead of `env`.
- **Commit author e-mail** (corporate domain, full legal name).
- Employer **system / vendor / squad names as bare words** (not domains, not secrets).
- Personal **hardware specs** used as examples.
- **Cloud-storage paths** embedding a personal e-mail.
- Absolute **home paths** in examples and commands.
- Internal **page/ticket IDs** and database schema names in docs.

## False positives to design around (do not just widen patterns)

DOI suffixes vs national-ID shapes; prose that *mentions* a key filename vs an
actual key path; npm `pkg@1.2.3` vs e-mail; base64 data URIs vs base64 credentials.
A blocked file is a review signal — the already-sanitised published version stays.

## If history must be rewritten

1. `git bundle create <backup>.bundle --all` first.
2. Rewrite content, then rewrite identities (mailmap → noreply address).
3. `git filter-repo` removes `origin`: re-add it, `fetch`, then push with
   `--force-with-lease`.
4. Purge unreachable objects (`reflog expire` + `gc --prune=now`), then re-scan
   **all** objects.
5. Tell the owner that force-pushing a public repo does **not** recall forks,
   clones or caches — and that any secret transmitted even once must be **rotated**.

See `knowledge/qoder_harness_integration_and_privacy_gate.md` for the full
rationale, observed leak vectors, and the macOS launchd/TCC automation caveats.
