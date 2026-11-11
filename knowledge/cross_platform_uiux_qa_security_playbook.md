# Cross-Platform UI/UX, QA, and Security Playbook

Extends `ui_ux_anti_slop_design_engineering.md` and `software_qa_and_testing_discipline.md`. Covers Windows desktop, macOS, web, and native mobile.

**Rule:** build → test → secure → verify. A green build is not proof of a working feature.

---

## 1. Platform matrix

| Dimension | Windows desktop | macOS | Web | Native mobile |
|---|---|---|---|---|
| Design language | Fluent / WinUI 3 | Apple HIG | WCAG 2.2 + brand system | Apple HIG / Material 3 |
| Window model | Resizable, min size, multi-window | Unified toolbar, traffic lights | Responsive viewport | Safe areas, notch, home indicator |
| Navigation | Sidebar + command palette | Menu bar + toolbar + shortcuts | URL, breadcrumbs, back/forward | Bottom tabs, swipe-back, bottom sheets |
| Density | High (12–13px body, 28–32px controls) | Medium-high | Medium (14–16px) | Touch-first, 44×44pt targets |
| Input | Mouse + keyboard + touch | Trackpad + keyboard | Mouse + keyboard + touch | Touch + gestures + haptics |
| Accessibility | UI Automation, Narrator | VoiceOver, Accessibility Inspector | ARIA, keyboard, screen readers | TalkBack, VoiceOver |
| Distribution | Installer + code signing | Notarization + hardened runtime | HTTPS + CSP | App Store / Play Store |

## 2. UI/UX foundations

1. **Design contract first** — `DESIGN.md` for tokens, `AGENTS.md` for behavior. No ad-hoc hex codes.
2. **Hierarchy through weight, spacing, and contrast** — not just font size.
3. **One primary action per screen**; destructive actions require confirmation and are visually distinct.
4. **Every async action has four states:** idle, loading, success, error with recovery.
5. **Empty states teach the next step**; error messages state cause + fix.
6. **Keyboard-first on desktop:** Tab order, Esc to close, Enter to submit, Cmd/Ctrl+K palette.
7. **Accessibility is a gate, not a nice-to-have:** contrast ≥ 4.5:1, visible focus, labels, reduced motion.
8. **Localization:** no text baked into images; allow 30–40% expansion; format dates/currency by locale.
9. **Dark mode** uses semantic tokens, not inverted colors.
10. **No dark patterns:** no fake urgency, hidden unsubscribe, confirmshaming, or forced continuity.

## 3. Usability testing

- **5 users per round** find most major issues; run 2–3 rounds.
- Task-based script: goal, starting state, success criteria, think-aloud.
- Measure: task success, time on task, error rate, SUS score.
- Heuristics: Nielsen 10 + platform HIG checklist.
- Instrument analytics only with consent; never log sensitive content.

## 4. QA strategy

### Test pyramid

| Layer | Share | What it proves |
|---|---:|---|
| Unit | 60–70% | Pure logic, edge cases, determinism |
| Integration / contract | 20–30% | DB, cache, queue, API contracts |
| E2E / UI | 10% | Critical user journeys |

Coverage is a signal, not a target. A 100% covered wrong assertion is worthless.

### Unit tests

- Arrange–Act–Assert; one behavior per test.
- No network, no real clock, no shared mutable state; inject time/randomness.
- Test boundaries: 0, negative, max, empty, unicode, null, timeout.
- Table-driven tests for parsers and validators.
- Snapshot tests only for stable, intentional output.

### Integration / contract tests

- Real database via container or ephemeral schema; migrations applied from zero.
- Kafka/Redis: topic/key/TTL contracts, duplicate delivery, retry, DLQ.
- API: schema validation, status codes, auth matrix, idempotency keys.
- Consumer-driven contracts (Pact) when multiple services consume the same API.

### E2E per platform

| Platform | Tools |
|---|---|
| Web | Playwright, Cypress, Testing Library, axe-core, Lighthouse |
| Windows | WinAppDriver, Appium, UI Automation, Accessibility Insights |
| macOS | XCUITest, Accessibility Inspector |
| Android | Espresso, UI Automator, Appium, Maestro |
| iOS | XCTest/XCUITest, Appium, Maestro |
| API | Postman/Newman, k6, Schemathesis |
| Visual | Percy, Applitools, BackstopJS |

Critical journeys: first run, onboarding, core action, save/export, error recovery, update, uninstall.

### Specialized testing

- **Performance:** cold start, memory, CPU, battery, large datasets, 10k-row tables.
- **Resilience:** network loss, timeout, disk full, permission denied, corrupted config.
- **Accessibility:** keyboard-only, screen reader, 200% zoom, high contrast.
- **Localization:** pseudo-locale, RTL, long strings, currency/date formats.
- **Install/update:** fresh install, upgrade over old version, downgrade, uninstall residue.
- **Security smoke:** authz, input validation, file path traversal, update signature.

## 5. QA process

1. Risk matrix: impact × likelihood × exposure.
2. Test plan per release: scope, environments, data, exit criteria.
3. Bug report: title, environment, steps, expected/actual, evidence, severity.
4. Severity: blocker, critical, major, minor, cosmetic.
5. Release gate: no open blocker/critical; all critical journeys pass; security scan clean.
6. Flaky tests are quarantined and fixed, never ignored.
7. Test data is synthetic or anonymized; never copy production PII.

## 6. Security testing

### Authorization first

Test only systems you own or have written permission to test. In Indonesia, unauthorized access is regulated by UU ITE; personal data by UU PDP. Define scope, rules of engagement, time window, and emergency contact before any active test. Never run destructive tests on production.

### Threat modeling (STRIDE)

Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege. Map each trust boundary: UI ↔ local service, app ↔ API, service ↔ DB, service ↔ broker, admin ↔ user data.

### Security test types

| Type | What | Tools |
|---|---|---|
| SAST | Source patterns, injection, secrets | Semgrep, SonarQube, CodeQL |
| SCA | Vulnerable dependencies | Trivy, Dependabot, OWASP Dependency-Check |
| Secrets | Keys/tokens in repo | gitleaks, TruffleHog |
| DAST | Running web app | OWASP ZAP, Burp Suite |
| API | Authn/authz, IDOR, rate limit | Schemathesis, Postman, Burp |
| Mobile | MASVS/MASTG | MobSF, Frida (authorized), apktool |
| Desktop | Signing, update, IPC, sandbox | Manual review + platform tools |
| Infrastructure | IaC, containers, CIS | Trivy, kube-bench, Checkov |

### Pentest phases

1. Scoping and legal authorization.
2. Reconnaissance and attack-surface inventory.
3. Threat model and test cases.
4. Controlled exploitation and evidence capture.
5. Post-exploitation impact analysis (authorized scope only).
6. Reporting with CVSS, reproduction, business impact, remediation.
7. Retest and closure.

### Platform-specific checks

**Web**
- OWASP Top 10 + WSTG + ASVS.
- AuthN/AuthZ on every endpoint; IDOR/BOLA tests.
- Input validation, output encoding, CSP, CSRF, SSRF, rate limits.
- Session/token lifecycle, cookie flags, logout invalidation.

**Windows desktop**
- Authenticode signing; verify update manifest signature.
- Least privilege; no unnecessary admin elevation.
- Local file permissions and path traversal.
- DLL search order hijacking; insecure IPC/named pipes.
- Electron: ASAR integrity, fuses, disabled `nodeIntegration`, context isolation.
- Tauri: capability allowlist, no broad shell access.

**macOS**
- Developer ID signing + notarization + hardened runtime.
- Sandbox entitlements; no unnecessary `com.apple.security.cs.disable-library-validation`.
- Keychain for secrets; launch agents/daemons least privilege.
- Gatekeeper and update integrity.

**Mobile**
- MASVS storage, crypto, auth, network, platform interaction, resilience.
- No secrets in APK/IPA; certificate pinning where appropriate.
- Deep link validation; exported components; WebView hardening.
- Jailbreak/root detection is a signal, not a security boundary.

**API/backend**
- AuthN/AuthZ, tenant isolation, IDOR.
- Injection (SQL/NoSQL/command/template).
- Deserialization, SSRF, file upload.
- Rate limits, replay protection, idempotency.
- Secrets management and rotation.

## 7. Reporting and remediation

- Severity via CVSS + business context.
- Evidence: request/response, screenshot, affected version, preconditions.
- Remediation SLA: critical 24–72h, high 7d, medium 30d, low 90d.
- Track accepted risks with owner and expiry.

## 8. Release gate checklist

- [ ] Critical journeys pass on all target platforms.
- [ ] Unit/integration/E2E green; no flaky quarantines unresolved.
- [ ] Accessibility audit passes (keyboard, screen reader, contrast).
- [ ] SAST/SCA/secrets scans clean or triaged.
- [ ] AuthZ matrix verified for every role.
- [ ] Install/update/uninstall tested with signed artifacts.
- [ ] Crash reporting and logs contain no PII/secrets.
- [ ] Rollback path tested.

## 9. Verified resources

UI/UX: https://www.nngroup.com/articles/ · https://m3.material.io/ · https://developer.apple.com/design/human-interface-guidelines/ · https://learn.microsoft.com/en-us/windows/apps/design/ · https://www.w3.org/WAI/WCAG22/quickref/ · https://lawsofux.com/ · https://web.dev/ · https://developer.android.com/guide/topics/ui

QA: https://martinfowler.com/articles/practical-test-pyramid.html · https://playwright.dev/ · https://docs.cypress.io/ · https://testing-library.com/ · https://pytest.org/ · https://go.dev/doc/tutorial/add-a-test · https://developer.apple.com/documentation/xctest · https://learn.microsoft.com/en-us/dotnet/core/testing/ · https://appium.io/ · https://k6.io/docs/ · https://webdriver.io/ · https://maestro.mobile.dev/ · https://github.com/microsoft/playwright-mcp · https://github.com/ChromeDevTools/chrome-devtools-mcp

Security: https://owasp.org/www-project-top-ten/ · https://owasp.org/www-project-web-security-testing-guide/ · https://owasp.org/www-project-application-security-verification-standard/ · https://mas.owasp.org/ · https://owasp.org/www-project-mobile-app-security/ · https://csrc.nist.gov/pubs/sp/800/115/final · https://attack.mitre.org/ · https://cwe.mitre.org/ · https://www.first.org/cvss/ · https://nvd.nist.gov/ · https://github.com/OWASP/mastg · https://github.com/mobsf/Mobile-Security-Framework-MobSF · https://github.com/semgrep/semgrep · https://github.com/aquasecurity/trivy · https://portswigger.net/burp · https://www.zaproxy.org/ · https://developer.android.com/privacy-and-security/security-tips · https://developer.apple.com/documentation/security · https://learn.microsoft.com/en-us/windows/security/ · https://support.apple.com/guide/security/welcome/web

Some official sites (CISA KEV, CDC, IMF, IDX, Cochrane, Annual Reviews) return 403 to bots but load in a browser.
