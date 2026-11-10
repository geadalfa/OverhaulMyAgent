# Microsoft Reality Check — Smart Tool Analysis

Source: https://github.com/microsoft/amplifier-smart-tool-reality-check
Version: v0.9.0 · MIT · Microsoft · verified 2026-11-10 (3 stars, new repo)
Spec: https://github.com/microsoft/amplifier-smart-tools

## 1. What it is

A Smart Tool that tests an application by **using it** — in a browser, on the desktop, or in a Digital Twin Universe — and returns a report with evidence for every finding: what was checked, what passed, what failed, and what was not checked.

It is designed for the moment after an agent says "it works" and the feature is still broken. It is **not** a unit-test replacement, a release gate, or a CI step. A check takes minutes; scripted tests remain the fast gate.

## 2. Architecture

- **Library is the tool.** Every capability lives in the library and is reachable from `lib.py`.
- **CLI, MCP, and app are thin wrappers** around the library.
- **Capabilities** live under `capabilities/<name>/` with prompts, templates, and a `SKILL.md`.
- **Core** holds the manifest and the router skill.
- **Smart Tool manifest:** `smart-tool.json` → `src/reality_check/SMART_TOOL.md`, CLI `reality-check`.
- **MCP:** `reality-check mcp` exposes checks to MCP Apps clients; `reality-check app` opens the browser app.
- **Skills:** `skills/reality-check/` is the agent skill installed with the tool.

## 3. CLI reference

```bash
reality-check check-software --request "Check that a new user can sign up" --target http://localhost:3000 --detach
reality-check read-check-activity --check-id CHECK_ID
reality-check steer-check --check-id CHECK_ID --message "Skip the settings pages"
reality-check cancel-check --check-id CHECK_ID
reality-check check-software --request "Check it again" --resume CHECK_ID
reality-check list-checks
reality-check read-check --check-id CHECK_ID
reality-check app
reality-check mcp
reality-check list-intelligence-models
reality-check install
```

Checks are saved in `.agents/reality-check` by default.

## 4. Installation

Prerequisites:
- `uv`
- one provider: GitHub Copilot CLI, Amplifier Agent, Codex CLI, or Claude Agent SDK.

```bash
npx skills add microsoft/amplifier-smart-tool-reality-check#v0.9.0
uv tool install "reality-check[all] @ git+https://github.com/microsoft/amplifier-smart-tool-reality-check@v0.9.0"
reality-check install
```

Computer use installs a pinned, hash-checked `cua-driver` release; browser checks install a pinned `agent-browser` and Chrome for Testing when needed. macOS needs Accessibility and Screen Recording permissions; WSL installs the Windows build.

## 5. What it is good at

- Verifying a feature or bug fix end-to-end after implementation.
- Exploratory UI checks: signup, messaging, settings consistency, spacing/icons/wording.
- Checking a dashboard loads within a time budget with no console errors.
- Producing screenshots and evidence that an agent can act on.
- Resuming a previous check after a fix.

## 6. Limitations and risks

- **Not a release gate** — minutes per check; keep unit/integration/E2E tests and CI.
- Provider costs and rate limits apply.
- v0.9.0, new repo, external contributions not currently open.
- Desktop control requires permissions and can interact with real apps.
- Check artifacts may contain screenshots, customer data, tokens, or internal URLs.
- Installing `cua-driver`/`agent-browser` downloads binaries; verify the pinned hash and permissions.
- The report says what was not checked; absence of a finding is not proof of correctness.

## 7. Privacy and internal-work boundary

Do **not** run Reality Check against employer or internal applications, real customer data, production admin panels, or anything under NDA without written authorization. Use local fixtures, synthetic accounts, and test environments. Keep `.agents/reality-check` out of any public repository; add it to `.gitignore` and to the GitHub publish denylist. Redact screenshots before sharing.

## 8. How Gemi should use it

1. After building one of User's desktop/web apps, start the app locally and run a **targeted** check (one user journey, one bug).
2. Use the report as evidence, not as a substitute for unit tests.
3. Pair with `cross_platform_uiux_qa_security_playbook.md` and `software-qa-and-ui-testing`.
4. Never publish `.agents/reality-check`, screenshots, or reports to GitHub.
5. Do not install the tool on User's machine without confirmation; it downloads pinned binaries and needs a provider.
6. If installed, prefer the `copilot` provider only if User has a Copilot subscription; otherwise use a provider User already pays for.

## 9. Links

- Repo: https://github.com/microsoft/amplifier-smart-tool-reality-check
- Smart Tools spec: https://github.com/microsoft/amplifier-smart-tools
- Digital Twin Universe: https://github.com/microsoft/amplifier-smart-tool-digital-twin-universe
- CLI reference: https://github.com/microsoft/amplifier-smart-tool-reality-check/blob/main/docs/02-cli.md
- Library reference: https://github.com/microsoft/amplifier-smart-tool-reality-check/blob/main/docs/01-library.md
