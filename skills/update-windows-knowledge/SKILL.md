---
name: update-windows-knowledge
description: Automatically sync rules, knowledge base, custom skills, and configurations from the Windows backup directory in Google Drive to macOS. Triggered by requests like 'tolong update pengetahuan dari windows' or 'sync windows knowledge'. Deterministically adapts Windows paths to macOS, protects system invariants, and refreshes cloud backups.
---

# Update Knowledge from Windows Backup

This skill automates syncing knowledge, rules, skills, and configuration files from the User's Windows workstation to macOS.

---

## 1. Trigger Keywords
- `"tolong update pengetahuan dari windows"`
- `"update pengetahuan dari windows"`
- `"sync windows knowledge"`
- Any command requesting synchronization of knowledge from Windows backup to macOS.

---

## 2. Backup Source Location
- **Google Drive Path on macOS:**
  ```text
  ~/Library/CloudStorage/GoogleDrive-<your-email>/Other computers/My Computer/Work/Backup Antigravity/Buat Windows
  ```
- **Target Files:**
  - `gemi-antigravity-config.zip` (primary priority)
  - `Gemi_AI_Knowledge_And_Rules.zip`

---

## 3. Deterministic Execution Workflow

When triggered, run the deterministic sync script using the `run_command` tool:

```bash
~/.gemini/scripts/sync_windows_knowledge.sh
```

### Script Execution Mechanism:
1. **Latest Archive Scan:** Scans the Windows backup directory for the newest ZIP archive based on modification timestamp.
2. **Staging Extraction:** Safely extracts archive contents to staging directory `/tmp/gemi_windows_sync_staging`.
3. **Smart Path Adaptation:**
   - Translates Windows paths (`~/.gemini/...` and `~\...`) to macOS paths (`~/.gemini/...`) for knowledge and configuration files.
   - Preserves specific hardware and Windows references (Ryzen Modern Processor, Dedicated GPU (12 GB+ VRAM), Windows registry, `DiagnoseMyDisk`) in relevant architectural documents.
4. **Knowledge Base Sync:** Copies new or updated markdown files to `~/.gemini/knowledge/`.
5. **Skills Sync:** Copies new/updated skill directories to `~/.gemini/config/skills/` and validates `skills.json`.
6. **MCP Schemas Sync:** Syncs tool definition schemas to `~/.gemini/antigravity/mcp/`.
7. **Global Rules Harmonization (`GEMINI.md`):**
   - Creates a timestamped backup of `config/GEMINI.md`.
   - Merges new sections without overwriting macOS invariants (backend repos in `~/Documents/`, mobile repos, keychain tokens, etc.).
8. **Cloud Backup Refresh:** Executes `~/.gemini/scripts/export_gemi_config.sh` to refresh the macOS ZIP bundle in Google Drive (`Backup Antigravity/gemi-antigravity-config.zip`).

---

## 4. Reporting Format for User

Upon script completion, report a clear, concise summary to User in Indonesian:
- Processed source ZIP file and its modification timestamp.
- Summary of new or updated knowledge files.
- Summary of new or updated custom skills.
- Confirmation that all paths have been adapted to macOS and the system remains stable.
