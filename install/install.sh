#!/usr/bin/env bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}   OverhaulMyAgent - Universal Multi-Harness Installer         ${NC}"
echo -e "${BLUE}================================================================${NC}"

TARGET_DIR="${1:-$HOME/.gemini}"

echo -e "${YELLOW}[*] Target Installation Directory: $TARGET_DIR${NC}"
mkdir -p "$TARGET_DIR/config/skills"
mkdir -p "$TARGET_DIR/knowledge"
mkdir -p "$TARGET_DIR/scripts"
mkdir -p "$TARGET_DIR/antigravity/mcp"

# Copy GEMINI.md
if [ -f "$SCRIPT_DIR/GEMINI.md" ]; then
    cp "$SCRIPT_DIR/GEMINI.md" "$TARGET_DIR/GEMINI.md"
    echo -e "${GREEN}  [✓] GEMINI.md installed.${NC}"
fi

# Copy Knowledge
if [ -d "$SCRIPT_DIR/knowledge" ]; then
    cp -r "$SCRIPT_DIR/knowledge/"* "$TARGET_DIR/knowledge/"
    echo -e "${GREEN}  [✓] Knowledge base installed.${NC}"
fi

# Copy Skills
if [ -d "$SCRIPT_DIR/skills" ]; then
    cp -r "$SCRIPT_DIR/skills/"* "$TARGET_DIR/config/skills/"
    echo -e "${GREEN}  [✓] Agent skills installed.${NC}"
fi

# Copy Tools
if [ -d "$SCRIPT_DIR/tools" ]; then
    cp -r "$SCRIPT_DIR/tools/"* "$TARGET_DIR/scripts/"
    chmod +x "$TARGET_DIR/scripts/"*.py 2>/dev/null || true
    echo -e "${GREEN}  [✓] Tools & scripts installed.${NC}"
fi

# Copy MCP Schemas
if [ -d "$SCRIPT_DIR/mcp/schemas" ]; then
    cp -r "$SCRIPT_DIR/mcp/schemas/"* "$TARGET_DIR/antigravity/mcp/"
    echo -e "${GREEN}  [✓] MCP tool schemas installed.${NC}"
fi

echo -e "\n${GREEN}[✓] OVERHAUL MY AGENT SUCCESSFULLY INSTALLED!${NC}"