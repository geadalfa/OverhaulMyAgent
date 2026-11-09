#!/usr/bin/env bash
#
# OverhaulMyAgent - Qoder harness installer (macOS / Linux).
#
# Installs this repository as a user-scope Qoder local plugin:
#   ~/.qoder/plugins/cache/local/overhaul-my-agent/<version>/
# then registers it in installed_plugins_v2.json and enables it in
# settings.json. Both files are merged (never blind-overwritten) and a
# timestamped .bak is kept. settings.json is always written as UTF-8
# WITHOUT a BOM - Qoder's strict MCP reader rejects BOM-prefixed files
# with SETTINGS_JSON_INVALID, silently disabling every user MCP server.
#
# Usage:
#   ./install/install_qoder.sh [--qoder-home DIR] [--dry-run]
#
set -euo pipefail

GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QODER_HOME="${QODER_HOME:-$HOME/.qoder}"
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --qoder-home) QODER_HOME="$2"; shift 2 ;;
    --dry-run)    DRY_RUN=1; shift ;;
    -h|--help)    sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo -e "${RED}Unknown option: $1${NC}" >&2; exit 2 ;;
  esac
done

MANIFEST="$SCRIPT_DIR/.qoder-plugin/plugin.json"
if [ ! -f "$MANIFEST" ]; then
  echo -e "${RED}[x] Missing $MANIFEST - run this from a repository checkout.${NC}" >&2
  exit 1
fi

PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
  echo -e "${RED}[x] python3 is required to merge Qoder JSON config safely.${NC}" >&2
  exit 1
fi

PLUGIN_NAME="$("$PY" -c 'import json,sys;print(json.load(open(sys.argv[1]))["name"])' "$MANIFEST")"
PLUGIN_VERSION="$("$PY" -c 'import json,sys;print(json.load(open(sys.argv[1]))["version"])' "$MANIFEST")"
DEST="$QODER_HOME/plugins/cache/local/$PLUGIN_NAME/$PLUGIN_VERSION"

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}   OverhaulMyAgent - Qoder Harness Installer                    ${NC}"
echo -e "${BLUE}================================================================${NC}"
echo -e "${YELLOW}[*] Repository : $SCRIPT_DIR${NC}"
echo -e "${YELLOW}[*] Qoder home : $QODER_HOME${NC}"
echo -e "${YELLOW}[*] Plugin     : ${PLUGIN_NAME}@local v${PLUGIN_VERSION}${NC}"
echo -e "${YELLOW}[*] Target     : $DEST${NC}"
[ "$DRY_RUN" -eq 1 ] && echo -e "${YELLOW}[*] DRY-RUN - nothing will be written.${NC}"

if [ ! -d "$QODER_HOME" ]; then
  echo -e "${RED}[x] $QODER_HOME not found. Install and start Qoder once, then re-run.${NC}" >&2
  exit 1
fi

# --- 1. Payload -------------------------------------------------------------
PAYLOAD_ITEMS=(skills knowledge tools core references QODER.md AGENTS.md README.md LICENSE)

echo -e "\n${BLUE}[*] Payload to install:${NC}"
for item in "${PAYLOAD_ITEMS[@]}"; do
  [ -e "$SCRIPT_DIR/$item" ] && echo "      + $item"
done
echo "      + .qoder-plugin/plugin.json"

if [ "$DRY_RUN" -eq 0 ]; then
  mkdir -p "$DEST"
  for item in "${PAYLOAD_ITEMS[@]}"; do
    [ -e "$SCRIPT_DIR/$item" ] || continue
    rm -rf "${DEST:?}/$item"
    cp -R "$SCRIPT_DIR/$item" "$DEST/$item"
  done
  mkdir -p "$DEST/.qoder-plugin"
  cp "$MANIFEST" "$DEST/.qoder-plugin/plugin.json"
  # core/ is the micro-kernel; expose it as references/ too so skills can
  # resolve it under either name.
  if [ -d "$SCRIPT_DIR/core" ]; then
    mkdir -p "$DEST/references"
    cp -R "$SCRIPT_DIR/core/." "$DEST/references/"
  fi
  echo -e "${GREEN}  [✓] Plugin payload installed.${NC}"
fi

# --- 2. Registry + settings merge ------------------------------------------
if [ "$DRY_RUN" -eq 0 ]; then
  "$PY" - "$QODER_HOME" "$DEST" "$PLUGIN_NAME" "$PLUGIN_VERSION" <<'PYEOF'
import json, os, shutil, sys, time

qoder_home, dest, name, version = sys.argv[1:5]
key = f"{name}@local"
stamp = time.strftime("%Y%m%d_%H%M%S")

def read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "rb") as fh:
        raw = fh.read()
    if raw[:3] == b"\xef\xbb\xbf":          # strip BOM: Qoder rejects it
        raw = raw[3:]
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        print(f"  ! refusing to merge into unparseable {path}: {exc}")
        sys.exit(1)

def detect_indent(raw):
    for line in raw.splitlines()[1:6]:
        stripped = line.lstrip(" ")
        if stripped.startswith('"'):
            n = len(line) - len(stripped)
            return 4 if n >= 4 else 2
    return 2

def write_json_nobom(path, data):
    indent = 2
    if os.path.exists(path):
        with open(path, "rb") as fh:
            indent = detect_indent(fh.read().decode("utf-8", "replace"))
        shutil.copy2(path, f"{path}.bak_qoder_install_{stamp}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:  # never a BOM
        json.dump(data, fh, indent=indent, ensure_ascii=False)
        fh.write("\n")

# --- plugin registry ---
reg_path = os.path.join(qoder_home, "plugins", "installed_plugins_v2.json")
reg = read_json(reg_path, {"version": 2, "plugins": {}})
reg.setdefault("version", 2)
plugins = reg.setdefault("plugins", {})
now = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
existing = (plugins.get(key) or [{}])[0]
entry = {
    "scope": "user",
    "installPath": dest,
    "version": version,
    "installedAt": existing.get("installedAt", now),
    "lastUpdated": now,
    "displayName": "OverhaulMyAgent",
}
plugins[key] = [entry]
write_json_nobom(reg_path, reg)
print(f"  [ok] registered {key} in installed_plugins_v2.json")

# --- settings: enable the plugin, preserve everything else ---
set_path = os.path.join(qoder_home, "settings.json")
settings = read_json(set_path, {})
enabled = settings.setdefault("enabledPlugins", {})
enabled[key] = True
write_json_nobom(set_path, settings)
print(f"  [ok] enabled {key} in settings.json")
PYEOF
  echo -e "${GREEN}  [✓] Registry + settings merged (backups kept as .bak_qoder_install_*).${NC}"
fi

# --- 3. MCP guidance (never auto-merged: templates hold placeholders) -------
echo -e "\n${BLUE}[*] MCP servers are NOT auto-installed.${NC}"
echo "    Review mcp/qoder_settings.template.json, fill in your own tokens, then"
echo "    merge the servers you want into $QODER_HOME/settings.json under \"mcpServers\"."
echo "    Remember: Qoder does not support the \"disabledTools\" key - drop it."

echo -e "\n${GREEN}[✓] OVERHAUL MY AGENT INSTALLED FOR QODER!${NC}"
echo -e "${YELLOW}[!] Restart Qoder so the plugin and its skills load.${NC}"
echo "    Verify: the skill listing should show ${PLUGIN_NAME}:plan-first and friends."
