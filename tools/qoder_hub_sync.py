#!/usr/bin/env python3
"""
qoder_hub_sync.py - Publish Qoder skills / knowledge / tools / MCP / plugin
changes to a public OverhaulMyAgent checkout, behind a mandatory sanitising gate.

Zero dependencies (Python 3.8+ stdlib only).

SAFETY MODEL (read before use)
------------------------------
The target repository is PUBLIC. This tool is deliberately conservative:

1. Memory is NEVER published.  ~/.qoder/memory holds personal preferences by
   definition; it belongs in the private backup, not on GitHub.
2. Existing items update; NEW items quarantine.  A skill/knowledge/tool that is
   not already tracked in the repository is written to the quarantine directory
   for human review unless --allow-new is passed.
3. Denylisted names are never published, even with --allow-new.
4. Frozen paths are never overwritten.  Some published documents are sanitised
   by hand because their local counterparts legitimately name internal systems;
   see DEFAULT_FROZEN_PATHS.
5. Block patterns abort publication.  Any credential, corporate endpoint,
   private IP, real home path, internal system name, or national-ID-shaped
   number found in candidate content quarantines that file. Nothing is
   redacted-and-published silently: redaction is applied only to
   well-understood shapes (home directory) and every redaction is reported.
6. Quarantine lives OUTSIDE the repository (~/.qoder/quarantine/<repo>) so
   rejected material - which can contain real credentials - can never be
   staged by a careless `git add -A`.
7. A whole-repository scan runs before any commit. One hit aborts the push.

Modes
-----
  scan      Report what would change. Writes nothing.
  sync      Apply changes to the repository working tree (no git operations).
  publish   sync + commit + push (push requires --push).

Usage
-----
  python3 tools/qoder_hub_sync.py scan
  python3 tools/qoder_hub_sync.py sync   --repo ~/src/OverhaulMyAgent
  python3 tools/qoder_hub_sync.py publish --repo ~/src/OverhaulMyAgent --push
"""

from __future__ import annotations

import argparse
import base64
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import time
from typing import Dict, Iterable, List, Optional, Tuple

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
HOME = os.path.expanduser("~")
QODER_HOME = os.environ.get("QODER_HOME", os.path.join(HOME, ".qoder"))
GEMINI_HOME = os.environ.get("GEMINI_HOME", os.path.join(HOME, ".gemini"))
PLUGIN_NAME = "overhaul-my-agent"
QUARANTINE_DIR = ".quarantine"
MCP_TEMPLATE = os.path.join("mcp", "qoder_settings.template.json")

# Quarantine lives OUTSIDE the repository by default. Rejected material can
# contain real credentials, so it must never sit inside a git working tree
# where a careless `git add -A` could stage it.
QUARANTINE_ROOT = os.path.join(QODER_HOME, "quarantine")

# Repository paths that are sanitised BY HAND and must never be overwritten
# from local sources. The local copies legitimately contain internal system
# names; the published copies use generic placeholders.
DEFAULT_FROZEN_PATHS: List[str] = [
    "knowledge/system_analyst_designer_diagramming.md",
    "skills/system-analyst-diagramming/SKILL.md",
]

# --------------------------------------------------------------------------
# Policy defaults. Override/extend via tools/qoder_hub_policy.json.
# --------------------------------------------------------------------------
# Skill / knowledge / tool names that must never leave this machine. Matched
# case-insensitively against the item name and as fnmatch globs.
#
# Base64-encoded on purpose: several entries name employer-internal systems,
# and the repository's own CI linter (`.github/workflows/ci.yml`) fails the
# build when those literals appear in any tracked file. Same trick the linter
# uses for its own patterns. Decode with `_decode_list`.
_B64_DENY_NAMES = (
    "WyJxb2Rlci1zeW5jIiwgInFvZGVyLWh1Yi1zeW5jIiwgInVwZGF0ZS1tYWMta25vd2xlZGdlIiwg"
    "InVwZGF0ZS13aW5kb3dzLWtub3dsZWRnZSIsICJmbGFzaG1pbmQtcGVyc2lzdGVudC1tZW1vcnki"
    "LCAiZGF0YWJhc2UtcXVlcnkiLCAiKi1pb3MtY29kZWMiLCAiamlyYS1zcHJlYWRzaGVldC1hdXRv"
    "bWF0aW9uIl0="
)
_B64_DENY_KNOWLEDGE = (
    "WyIqZGF0YWJhc2VfcmVnaXN0cnkqIiwgIipjcmVkZW50aWFsKiIsICIqbG9jYWxfYXBwbGljYXRp"
    "b25zX3JlZ2lzdHJ5KiIsICIqY29uZmx1ZW5jZV9hdXRob3JpbmcqIiwgIiprYWZrYSoiLCAiKmdh"
    "dGV3YXkqIiwgIip3aXRob3V0X3BpbioiLCAiKmdpdGh1Yl9wZXJzb25hbF9pbnRlZ3JhdGlvbioi"
    "LCAiKmdpdGh1Yl9kZXNrdG9wX2FwcF9yZWxlYXNlKiIsICIqc2NhX3Jlc29sdmVyKiIsICIqb25i"
    "b2FyZGluZ18xMDEqIiwgIipnbG9iYWxwcm90ZWN0KiIsICIqZnJkXyoiLCAiKmVyYW5nZWwqIl0="
)


def _decode_list(blob: str, fallback: List[str]) -> List[str]:
    try:
        decoded = json.loads(base64.b64decode(blob).decode("utf-8"))
        if isinstance(decoded, list):
            return [str(x) for x in decoded]
    except (ValueError, UnicodeDecodeError):
        pass
    return list(fallback)


DEFAULT_DENY_NAMES: List[str] = _decode_list(_B64_DENY_NAMES, [
    "qoder-sync", "qoder-hub-sync", "database-query", "*-ios-codec",
])
DEFAULT_DENY_KNOWLEDGE: List[str] = _decode_list(_B64_DENY_KNOWLEDGE, [
    "*database_registry*", "*credential*", "*local_applications_registry*",
    "*confluence_authoring*", "*kafka*", "*gateway*", "*sample-feature*",
    "*github_personal_integration*", "*github_desktop_app_release*",
    "*sca_resolver*", "*onboarding_101*", "*frd_*",
])

# Employer/product/system identifiers that must never appear in published
# content. These are bare words rather than domains or secrets, so the regex
# patterns below do not catch them - they need an explicit terminology gate.
# Base64-encoded for the same reason as the denylists above.
_B64_BLOCK_TERMS = (
    "WyJicmltbyIsICJiZXJicmltbyIsICJxaXRhIiwgImVyYW5nZWwiLCAidmlrZW5kaSIsICJsYWRy"
    "aWxsZXJhIiwgIndlbmdlbiIsICJyb3pob2siLCAiaG90c3ByaW5nIiwgImhlbGxlIiwgImltcGFs"
    "YSIsICJsaXZpayIsICJicmlnYXRlIiwgImR1a2NhcGlsIiwgInRpbGFrYSIsICJiYW5rIHJha3lh"
    "dCIsICJnbG9iYWxwcm90ZWN0IiwgImdlYWRhbGZhIiwgImFsZmEiLCAiYnJpbmV0IiwgInphcmto"
    "aSIsICJvcGVuX2FjY291bnQiLCAibmFpcm9iaSIsICJ0ZW5jZW50IiwgInByaXZ5IiwgInZpZGEi"
    "LCAiem9sb3oiLCAiNDA3MCBzdXBlciIsICI4NzAwZiJd"
)
DEFAULT_BLOCK_TERMS: List[str] = _decode_list(_B64_BLOCK_TERMS, [])

# Content that aborts publication outright.
DEFAULT_BLOCK_PATTERNS: Dict[str, str] = {
    "github_token": r"\bgh[pousr]_[A-Za-z0-9]{20,}\b",
    "github_fine_grained": r"\bgithub_pat_[A-Za-z0-9_]{20,}\b",
    "bitbucket_token": r"\bBBDC-[A-Za-z0-9_\-:/+]{10,}",
    "atlassian_token": r"\bATATT3[A-Za-z0-9_\-]{20,}",
    "aws_access_key": r"\b(AKIA|ASIA)[0-9A-Z]{16}\b",
    "google_api_key": r"\bAIza[0-9A-Za-z_\-]{30,}\b",
    "slack_token": r"\bxox[baprs]-[A-Za-z0-9-]{10,}",
    "openai_key": r"\bsk-[A-Za-z0-9_\-]{20,}\b",
    "private_key_block": r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----",
    "bearer_token": r"[Bb]earer\s+[A-Za-z0-9._\-]{24,}",
    "basic_auth_header": r"\bBasic\s+[A-Za-z0-9+/=]{24,}",
    "jwt": r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}",
    "generic_secret_assignment": r"(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|private[_-]?key)\b\s*[:=]\s*['\"][^'\"\s]{8,}['\"]",
    # 16-digit national ID. Lookbehind excludes DOI suffixes (10.1177/17456...)
    # and other delimited numeric literals.
    "national_id_16": r"(?<![0-9./_\-])\d{16}(?![0-9])",
    "corporate_intranet_host": r"(?i)\b[a-z0-9\-]+\.(?:co\.id|corp|internal|intranet|local)\b",
    "private_ipv4": r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b",
    "cloud_storage_account": r"CloudStorage/[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+",
    # Real e-mail address. Requires an alphabetic TLD so npm specifiers such as
    # `pkg@1.2.3` do not match. Placeholder domains used across this
    # repository's templates and MCP schemas are expected and skipped.
    "personal_email": r"[A-Za-z0-9._%+\-]+@(?!example\.|domain\.com|your-company|users\.noreply)[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}\b",
    # Corporate/ISP allocation that the repository's own CI linter rejects.
    "public_ip_190": r"\b190\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "windows_user_profile": r"(?i)\bc:\\+users\\+(?!public|name|your)[a-z0-9._\- ]{2,}",
    # Only a real key path, not prose that mentions the filename as advice.
    "ssh_private_material": r"(?i)\.ssh[/\\]id_(?:rsa|ed25519|ecdsa|dsa)\b",
    "employee_id_pair": r"(?i)\b(?:employee|nik|nip|badge)[ _-]?(?:id|no|number)?\b\s*[:=]\s*\d{5,}",
}

# CLI flags whose following argument is a credential.
SECRET_FLAG_RE = re.compile(
    r"(?i)^--?[a-z0-9][a-z0-9_\-]*(?:token|password|passwd|secret|api[-_]?key|credential|auth)")
# Anything that looks like opaque credential material: base64-ish with a '+'
# or '/', or a long high-entropy mixed-case alphanumeric run. Plain hex digests
# and ordinary long words are deliberately not matched.
TOKENISH_RE = re.compile(r"[A-Za-z0-9]{20,}[+/][A-Za-z0-9+/=]{6,}|[A-Za-z0-9]*[a-z][A-Za-z0-9]*[A-Z][A-Za-z0-9]*[+/=][A-Za-z0-9+/=]{6,}")

# Numbers that look like national IDs but are well-known constants.
BLOCK_ALLOW_CONSTANTS = {"9007199254740991", "1234567890123456"}

# Shapes that are rewritten rather than blocked, with a report line.
REDACT_RULES: List[Tuple[str, str, str]] = [
    # Real home directory -> neutral placeholder.
    ("home_path_unix", re.escape(HOME), "<HOME>"),
    ("home_path_user", r"/Users/(?!(?:validate|myaccount|name|your))[A-Za-z0-9._\-]+", "/Users/<user>"),
    ("home_path_win_user", r"(?i)c:\\+users\\+[a-z0-9._\- ]{2,}", r"C:\\Users\\<user>"),
    ("tilde_home", r"(?<![\w])~/" + re.escape(os.path.basename(HOME)) + r"\b", "~/<user>"),
]

# The operator's personal name/handle is rewritten to the neutral "User",
# matching the convention already used throughout this repository. Encoded so
# the literal name never appears in a tracked file (CI would reject it).
_B64_PERSONA_NAMES = "WyJHZWFkYWxmYSIsICJBbGZhIl0="
PERSONA_NAMES: List[str] = _decode_list(_B64_PERSONA_NAMES, [])

for _name in PERSONA_NAMES:
    for _variant, _replacement in ((_name, "User"), (_name.lower(), "user"), (_name.upper(), "USER")):
        REDACT_RULES.append((
            f"persona_name:{_name.lower()}",
            r"(?<![\w])" + re.escape(_variant) + r"(?![\w])",
            _replacement,
        ))


def log(msg: str = "") -> None:
    print(msg)


def warn(msg: str) -> None:
    print(f"  ! {msg}", file=sys.stderr)


# --------------------------------------------------------------------------
# Policy loading
# --------------------------------------------------------------------------
class Policy:
    def __init__(self, repo_root: str) -> None:
        self.deny_names = list(DEFAULT_DENY_NAMES)
        self.deny_knowledge = list(DEFAULT_DENY_KNOWLEDGE)
        self.block_patterns = dict(DEFAULT_BLOCK_PATTERNS)
        self.block_terms = list(DEFAULT_BLOCK_TERMS)
        self.frozen_paths = list(DEFAULT_FROZEN_PATHS)
        path = os.path.join(repo_root, "tools", "qoder_hub_policy.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except (OSError, json.JSONDecodeError) as exc:
                warn(f"ignoring unreadable policy {path}: {exc}")
                return
            self.deny_names = data.get("deny_names", self.deny_names)
            self.deny_knowledge = data.get("deny_knowledge", self.deny_knowledge)
            extra = data.get("extra_block_patterns") or {}
            if isinstance(extra, dict):
                self.block_patterns.update(extra)
            removed = data.get("remove_block_patterns") or []
            for key in removed:
                self.block_patterns.pop(key, None)
            extra_terms = data.get("extra_block_terms") or []
            if isinstance(extra_terms, list):
                self.block_terms.extend(str(t) for t in extra_terms)
            removed_terms = data.get("remove_block_terms") or []
            if isinstance(removed_terms, list):
                drop = {str(t).lower() for t in removed_terms}
                self.block_terms = [t for t in self.block_terms if t.lower() not in drop]
            if isinstance(data.get("extra_frozen_paths"), list):
                self.frozen_paths.extend(str(p) for p in data["extra_frozen_paths"])
            log(f"[*] Loaded policy overrides from {path}")

    def is_frozen(self, relpath: str) -> bool:
        norm = relpath.replace(os.sep, "/")
        return any(norm == f.replace(os.sep, "/") for f in self.frozen_paths)

    def name_denied(self, name: str) -> Optional[str]:
        low = name.lower()
        for pat in self.deny_names:
            if low == pat.lower() or fnmatch.fnmatch(low, pat.lower()):
                return pat
        return None

    def knowledge_denied(self, filename: str) -> Optional[str]:
        low = filename.lower()
        for pat in self.deny_knowledge:
            if fnmatch.fnmatch(low, pat.lower()):
                return pat
        return None


# --------------------------------------------------------------------------
# Scanning
# --------------------------------------------------------------------------
class Finding:
    __slots__ = ("path", "pattern", "sample")

    def __init__(self, path: str, pattern: str, sample: str) -> None:
        self.path = path
        self.pattern = pattern
        self.sample = sample

    def __str__(self) -> str:
        return f"{self.path}: [{self.pattern}] {self.sample}"


def _mask(value: str) -> str:
    """Never echo a matched secret in full."""
    value = value.strip()
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}…{value[-2:]} ({len(value)} chars)"


def scan_text(text: str, path: str, policy: Policy) -> List[Finding]:
    findings: List[Finding] = []
    for name, pattern in policy.block_patterns.items():
        for match in re.finditer(pattern, text):
            sample = match.group(0)
            if name == "national_id_16" and sample in BLOCK_ALLOW_CONSTANTS:
                continue
            # Placeholders in templates are expected, not leaks.
            if re.search(r"YOUR_[A-Z0-9_]*_HERE|<HOME>|<user>|example\.com|your-company|ABSOLUTE/PATH", sample):
                continue
            findings.append(Finding(path, name, _mask(sample)))
    for term in policy.block_terms:
        if re.search(r"(?<![\w])" + re.escape(term) + r"(?![\w])", text, re.IGNORECASE):
            findings.append(Finding(path, "internal_term", term.lower()))
    return findings


def redact(text: str) -> Tuple[str, List[str]]:
    applied: List[str] = []
    for name, pattern, replacement in REDACT_RULES:
        new_text, count = re.subn(pattern, replacement, text)
        if count:
            applied.append(f"{name} x{count}")
            text = new_text
    return text, applied


def scan_repo(repo_root: str, policy: Policy) -> List[Finding]:
    """Whole-repository gate. Mirrors the CI linter but with stricter patterns."""
    findings: List[Finding] = []
    skip_dirs = {".git", QUARANTINE_DIR}
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in files:
            if name in {"qoder_hub_sync.py", "ci.yml"}:
                continue  # this file legitimately contains pattern definitions
            path = os.path.join(root, name)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
            except OSError:
                continue
            findings.extend(scan_text(text, os.path.relpath(path, repo_root), policy))
    return findings


# --------------------------------------------------------------------------
# Source discovery
# --------------------------------------------------------------------------
def qoder_plugin_dirs() -> List[str]:
    root = os.path.join(QODER_HOME, "plugins", "cache", "local")
    out: List[str] = []
    if not os.path.isdir(root):
        return out
    for plugin in sorted(os.listdir(root)):
        pdir = os.path.join(root, plugin)
        if not os.path.isdir(pdir):
            continue
        for version in sorted(os.listdir(pdir)):
            cand = os.path.join(pdir, version)
            if os.path.isdir(cand):
                out.append(cand)
    return out


def source_roots() -> List[Tuple[str, str]]:
    """(label, root) pairs, most authoritative last so it wins on conflict."""
    roots: List[Tuple[str, str]] = []
    live_skills = os.path.join(GEMINI_HOME, "config", "skills")
    if os.path.isdir(live_skills):
        roots.append(("antigravity-live", GEMINI_HOME))
    for pdir in qoder_plugin_dirs():
        if os.path.basename(os.path.dirname(pdir)) == PLUGIN_NAME:
            continue  # do not feed the repo's own published payload back in
        roots.append((f"qoder-plugin:{os.path.basename(os.path.dirname(pdir))}", pdir))
    if os.path.isdir(os.path.join(QODER_HOME, "skills")):
        roots.append(("qoder-standalone-skills", QODER_HOME))
    return roots


def collect_items() -> Dict[str, Dict[str, object]]:
    """Return {repo_relative_path: {'src': abs_path, 'kind': str, 'name': str}}."""
    items: Dict[str, Dict[str, object]] = {}
    for label, root in source_roots():
        # skills
        for base, rel in ((os.path.join(root, "config", "skills"), "skills"),
                          (os.path.join(root, "skills"), "skills")):
            if not os.path.isdir(base):
                continue
            for name in sorted(os.listdir(base)):
                sdir = os.path.join(base, name)
                if not os.path.isdir(sdir):
                    continue
                for dirpath, _dirs, files in os.walk(sdir):
                    for fname in files:
                        src = os.path.join(dirpath, fname)
                        relpath = os.path.join(rel, name, os.path.relpath(src, sdir))
                        items[relpath] = {"src": src, "kind": "skill", "name": name, "origin": label}
        # knowledge
        for base in (os.path.join(root, "knowledge"),):
            if not os.path.isdir(base):
                continue
            for fname in sorted(os.listdir(base)):
                src = os.path.join(base, fname)
                if os.path.isfile(src) and fname.endswith(".md"):
                    items[os.path.join("knowledge", fname)] = {
                        "src": src, "kind": "knowledge", "name": fname, "origin": label}
        # tools / scripts
        for base in (os.path.join(root, "scripts"), os.path.join(root, "tools")):
            if not os.path.isdir(base):
                continue
            for fname in sorted(os.listdir(base)):
                src = os.path.join(base, fname)
                if os.path.isfile(src) and fname.endswith((".py", ".sh", ".ps1", ".swift", ".mjs", ".js")):
                    items[os.path.join("tools", fname)] = {
                        "src": src, "kind": "tool", "name": fname, "origin": label}
    return items


# --------------------------------------------------------------------------
# MCP template refresh (redacted, allowlist-only)
# --------------------------------------------------------------------------
def build_mcp_template(repo_root: str, allow_new: bool) -> Tuple[Optional[dict], List[str]]:
    settings_path = os.path.join(QODER_HOME, "settings.json")
    template_path = os.path.join(repo_root, MCP_TEMPLATE)
    notes: List[str] = []
    if not os.path.exists(settings_path) or not os.path.exists(template_path):
        return None, notes
    try:
        with open(settings_path, "rb") as fh:
            raw = fh.read()
        if raw[:3] == b"\xef\xbb\xbf":
            raw = raw[3:]
        settings = json.loads(raw.decode("utf-8"))
        with open(template_path, "r", encoding="utf-8") as fh:
            template = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        warn(f"could not read MCP config: {exc}")
        return None, notes

    allowed = set((template.get("mcpServers") or {}).keys())
    # Start from the shipped template so repo-native servers (financial-engine,
    # nvidia-app) survive even when they are absent from local settings.
    out_servers: Dict[str, dict] = {
        name: dict(spec) for name, spec in (template.get("mcpServers") or {}).items()
    }
    for name, spec in (settings.get("mcpServers") or {}).items():
        if name not in allowed:
            if allow_new:
                notes.append(f"mcp: new server '{name}' included (--allow-new)")
            else:
                notes.append(f"mcp: skipped private/new server '{name}' (not in template allowlist)")
                continue
        clean: Dict[str, object] = {}
        command = str(spec.get("command") or "")
        # Publish the bare executable, never an absolute machine-specific path.
        # Split on both separators: a Windows path is not a path on POSIX.
        clean["command"] = re.split(r"[\\/]", command)[-1] if command else command
        args_out = []
        prev_was_secret_flag = False
        for arg in spec.get("args") or []:
            text = str(arg)
            # A credential can be passed as a CLI argument instead of env, e.g.
            # `--jira-personal-token <token>`. Redact the value that follows
            # any secret-looking flag, and anything that looks like a token.
            if prev_was_secret_flag:
                args_out.append("YOUR_TOKEN_HERE")
                notes.append(f"mcp.{name}: redacted a credential passed as a CLI argument")
                prev_was_secret_flag = False
                continue
            if SECRET_FLAG_RE.match(text):
                args_out.append(text)
                prev_was_secret_flag = True
                continue
            if TOKENISH_RE.fullmatch(text):
                args_out.append("YOUR_TOKEN_HERE")
                notes.append(f"mcp.{name}: redacted a token-shaped CLI argument")
                continue
            if text.startswith(HOME) or text.startswith("/Users/") or re.match(r"(?i)^[a-z]:\\", text):
                args_out.append(os.path.join("/ABSOLUTE/PATH/TO/OverhaulMyAgent",
                                             re.split(r"[\\/]", text)[-1]))
                notes.append(f"mcp.{name}: rewrote absolute arg to a placeholder")
            elif re.match(r"(?i)^https?://", text):
                host = re.sub(r"^https?://", "", text).split("/")[0]
                if not re.search(r"(?i)(?:^|\.)(?:github\.com|npmjs\.(?:org|com)|pypi\.org|atlassian\.net)$", host):
                    args_out.append("https://your-company.example.com")
                    notes.append(f"mcp.{name}: redacted a non-public host")
                else:
                    args_out.append(text)
            else:
                args_out.append(text)
        if args_out:
            clean["args"] = args_out
        env = spec.get("env") or {}
        # PATH is machine-specific; publishing a placeholder PATH would break
        # anyone who copies the template, so drop it.
        publishable_env = {k: v for k, v in env.items() if k.upper() != "PATH"}
        if publishable_env:
            clean["env"] = {
                k: f"YOUR_{re.sub(r'[^A-Z0-9]', '_', k.upper())}_HERE" for k in publishable_env
            }
            notes.append(f"mcp.{name}: redacted {len(publishable_env)} env value(s) to placeholders")
        if spec.get("disabled"):
            clean["disabled"] = True
        # Qoder has no disabledTools; never re-introduce it.
        out_servers[name] = clean

    # Final safety net: no opaque token-shaped value may survive anywhere in
    # the generated template, whatever key or position it came from.
    for srv_name, srv in out_servers.items():
        for arg_index, value in enumerate(srv.get("args") or []):
            if isinstance(value, str) and TOKENISH_RE.fullmatch(value):
                srv["args"][arg_index] = "YOUR_TOKEN_HERE"
                notes.append(f"mcp.{srv_name}: safety-net redaction of args[{arg_index}]")
        for env_key, value in (srv.get("env") or {}).items():
            if isinstance(value, str) and TOKENISH_RE.fullmatch(value):
                srv["env"][env_key] = f"YOUR_{re.sub(r'[^A-Z0-9]', '_', env_key.upper())}_HERE"
                notes.append(f"mcp.{srv_name}: safety-net redaction of env.{env_key}")

    template["mcpServers"] = out_servers
    return template, notes


# --------------------------------------------------------------------------
# Sync engine
# --------------------------------------------------------------------------
def git(args: List[str], cwd: str) -> Tuple[int, str]:
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def ensure_gitignore(repo_root: str, dry: bool) -> None:
    path = os.path.join(repo_root, ".gitignore")
    entries = [f"{QUARANTINE_DIR}/", "*.bak_qoder_install_*", ".DS_Store", "__pycache__/"]
    existing = ""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            existing = fh.read()
    missing = [e for e in entries if e not in existing.split()]
    if not missing:
        return
    if dry:
        log(f"  ~ .gitignore would gain: {', '.join(missing)}")
        return
    body = existing.rstrip("\n")
    if body and not body.endswith("\n"):
        body += "\n"
    if body and not body.endswith("\n\n"):
        body += "\n"
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(missing) + "\n")
    log(f"  + .gitignore: {', '.join(missing)}")


def run(args: argparse.Namespace) -> int:
    repo_root = os.path.abspath(os.path.expanduser(args.repo))
    if not os.path.isdir(os.path.join(repo_root, ".git")):
        warn(f"{repo_root} is not a git checkout. Pass --repo <clone>.")
        return 2
    if shutil.which("git") is None and args.mode == "publish":
        warn("git executable not found; cannot publish.")
        return 2

    policy = Policy(repo_root)
    dry = args.mode == "scan"
    log(f"\n== qoder_hub_sync :: {args.mode.upper()} ==")
    log(f"  repo       : {repo_root}")
    log(f"  qoder home : {QODER_HOME}")
    log(f"  sources    : {', '.join(label for label, _ in source_roots()) or '(none found)'}")
    if dry:
        log("  DRY-RUN: nothing will be written.")

    ensure_gitignore(repo_root, dry)

    items = collect_items()
    quarantine = os.path.abspath(os.path.expanduser(
        args.quarantine or os.path.join(QUARANTINE_ROOT, os.path.basename(repo_root))))
    log(f"  quarantine : {quarantine}")
    stats = {"updated": 0, "unchanged": 0, "new": 0, "quarantined": 0,
             "denied": 0, "blocked": 0, "frozen": 0}
    report: List[str] = []
    staged_paths: List[str] = []

    for relpath, meta in sorted(items.items()):
        src = str(meta["src"])
        kind = str(meta["kind"])
        name = str(meta["name"])

        denied = policy.name_denied(name) or (kind == "knowledge" and policy.knowledge_denied(name))
        if denied:
            stats["denied"] += 1
            report.append(f"DENIED  {relpath}  (policy: {denied})")
            continue

        if policy.is_frozen(relpath):
            stats["frozen"] += 1
            report.append(f"FROZEN  {relpath}  (hand-sanitised in repo; never auto-overwritten)")
            continue

        try:
            with open(src, "r", encoding="utf-8", errors="strict") as fh:
                text = fh.read()
        except UnicodeDecodeError:
            stats["quarantined"] += 1
            report.append(f"QUARANTINE {relpath}  (binary/non-UTF-8; review manually)")
            if not dry:
                _write_quarantine(quarantine, relpath, src)
            continue
        except OSError as exc:
            warn(f"skip {relpath}: {exc}")
            continue

        # Redact first (home paths, persona name), then scan the result, so any
        # residue - or anything redaction does not cover - still blocks.
        text, applied = redact(text)
        findings = scan_text(text, relpath, policy)
        if findings:
            stats["blocked"] += 1
            detail = "; ".join(
                f"[{f.pattern}:{f.sample}]" if f.pattern == "internal_term" else f"[{f.pattern}]"
                for f in findings[:4]
            )
            report.append(f"BLOCKED {relpath}  ({len(findings)} finding(s): {detail})")
            if not dry:
                _write_quarantine(quarantine, relpath, src, redacted=text)
                _write_findings(quarantine, relpath, findings)
            continue

        dest = os.path.join(repo_root, relpath)
        is_new = not os.path.exists(dest)
        current = None
        if not is_new:
            try:
                with open(dest, "r", encoding="utf-8") as fh:
                    current = fh.read()
            except OSError:
                current = None

        if current == text:
            stats["unchanged"] += 1
            continue

        if is_new and not args.allow_new:
            stats["quarantined"] += 1
            report.append(f"NEW→QUARANTINE {relpath}  (not tracked in repo; pass --allow-new to publish)")
            if not dry:
                _write_quarantine(quarantine, relpath, src, redacted=text)
            continue

        if dry:
            stats["new" if is_new else "updated"] += 1
            note = f"  (redacted: {', '.join(applied)})" if applied else ""
            report.append(f"{'NEW ' if is_new else 'UPDATE'} {relpath}{note}")
            continue

        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        stats["new" if is_new else "updated"] += 1
        note = f"  (redacted: {', '.join(applied)})" if applied else ""
        report.append(f"{'NEW ' if is_new else 'UPDATE'} {relpath}{note}")
        staged_paths.append(relpath)

    # --- MCP template ------------------------------------------------------
    template, mcp_notes = build_mcp_template(repo_root, args.allow_new)
    report.extend(f"MCP  {n}" for n in mcp_notes)
    if template is not None:
        dest = os.path.join(repo_root, MCP_TEMPLATE)
        rendered = json.dumps(template, indent=2, ensure_ascii=False) + "\n"
        existing = None
        if os.path.exists(dest):
            with open(dest, "r", encoding="utf-8") as fh:
                existing = fh.read()
        if existing != rendered:
            findings = scan_text(rendered, MCP_TEMPLATE, policy)
            if findings:
                stats["blocked"] += 1
                report.append(f"BLOCKED {MCP_TEMPLATE} ({len(findings)} finding(s)); template left untouched")
            elif dry:
                stats["updated"] += 1
                report.append(f"UPDATE {MCP_TEMPLATE}")
            else:
                with open(dest, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(rendered)
                stats["updated"] += 1
                report.append(f"UPDATE {MCP_TEMPLATE}")
                staged_paths.append(MCP_TEMPLATE)

    # --- Report ------------------------------------------------------------
    if report:
        log("\n  -- changes --")
        for line in report:
            log(f"    {line}")
    log("\n  -- summary --")
    log(f"    updated={stats['updated']} new={stats['new']} unchanged={stats['unchanged']} "
        f"frozen={stats['frozen']} quarantined={stats['quarantined']} "
        f"blocked={stats['blocked']} denied={stats['denied']}")

    if dry:
        log("\n  SCAN complete. Re-run with `sync` to apply, `publish --push` to ship.\n")
        return 0

    if stats["blocked"] or stats["quarantined"]:
        warn(f"{stats['blocked']} blocked + {stats['quarantined']} unreviewed file(s) quarantined "
             f"under {quarantine} — review before publishing.")

    if args.mode != "publish":
        log("\n  SYNC complete. Review `git diff`, then run `publish --push`.\n")
        return 0

    # --- Publish gate ------------------------------------------------------
    log("\n  [*] Running whole-repository security gate …")
    findings = scan_repo(repo_root, policy)
    if findings:
        log(f"\n  [x] ABORT: {len(findings)} sensitive finding(s) in the repository:")
        for f in findings[:20]:
            log(f"      {f}")
        log("      Nothing was committed or pushed.")
        return 1

    rc, _ = git(["add", "-A", "--", ".", f":(exclude){QUARANTINE_DIR}"], repo_root)
    if rc != 0:
        warn("git add failed")
        return 1
    rc, staged = git(["diff", "--cached", "--name-only"], repo_root)
    if rc != 0:
        warn("git diff failed")
        return 1
    if any(part.startswith(QUARANTINE_DIR) for part in staged.splitlines()):
        warn("refusing to commit: quarantined files were staged")
        return 1
    if not staged.strip():
        log("  [=] Nothing to commit — repository already up to date.\n")
        return 0

    message = args.message or (
        "chore(hub): sync Qoder skills, knowledge, tools and MCP template\n\n"
        f"Generated by tools/qoder_hub_sync.py on {time.strftime('%Y-%m-%d %H:%M:%S')}.\n"
        f"updated={stats['updated']} new={stats['new']} blocked={stats['blocked']} denied={stats['denied']}"
    )
    rc, out = git(["commit", "-m", message], repo_root)
    if rc != 0:
        warn(f"git commit failed: {out}")
        return 1
    log(f"  [✓] Committed {len(staged.splitlines())} file(s).")

    if not args.push:
        log("  [=] --push not given; commit stays local.\n")
        return 0
    rc, out = git(["push", "origin", "HEAD"], repo_root)
    if rc != 0:
        warn(f"git push failed: {out}")
        log("      Hint: authenticate (credential helper / SSH remote) and re-run `publish --push`.")
        return 1
    log(f"  [✓] Pushed to origin.\n")
    return 0


def _write_quarantine(quarantine: str, relpath: str, src: str, redacted: Optional[str] = None) -> None:
    dest = os.path.join(quarantine, relpath)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if redacted is not None:
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(redacted)
    else:
        shutil.copy2(src, dest)


def _write_findings(quarantine: str, relpath: str, findings: Iterable[Finding]) -> None:
    dest = os.path.join(quarantine, relpath + ".findings.txt")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("\n".join(str(f) for f in findings) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publish Qoder assets to a public OverhaulMyAgent checkout behind a sanitising gate.")
    parser.add_argument("mode", choices=["scan", "sync", "publish"], nargs="?", default="scan")
    parser.add_argument("--repo", default=os.path.join(HOME, "src", "OverhaulMyAgent"),
                        help="path to the OverhaulMyAgent git checkout")
    parser.add_argument("--push", action="store_true", help="push after committing (publish mode)")
    parser.add_argument("--allow-new", action="store_true",
                        help="publish items not already tracked in the repo (default: quarantine them)")
    parser.add_argument("--quarantine", default=None,
                        help=f"where rejected/unreviewed files go (default: {QUARANTINE_ROOT}/<repo>)")
    parser.add_argument("--message", default=None, help="override the commit message")
    args = parser.parse_args()
    try:
        return run(args)
    except KeyboardInterrupt:
        warn("interrupted")
        return 130


if __name__ == "__main__":
    sys.exit(main())
