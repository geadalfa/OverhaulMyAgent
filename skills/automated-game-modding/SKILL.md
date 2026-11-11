---
name: automated-game-modding
description: Discover installed games, validate mod compatibility against executable versions, resolve dependency trees, stage archives, and safely deploy/undeploy mods with transactional SHA-256 rollback and live in-game editing support.
---

# Automated Game Modding & Crash-Free Safety Skill

Use this skill whenever User requests discovering installed PC games, downloading, installing, verifying, or customizing game mods (from Nexus Mods, GitHub, Steam Workshop, Modrinth, etc.) without corrupting vanilla files or causing crash-to-desktop (CTD) loops.

---

## 1. Safety Invariants (Strict Non-Destructive Modding)

Every modding task executed by Gemi MUST follow these 5 core rules:

| Invariant | Mandatory Constraint | Rationale |
| :--- | :--- | :--- |
| **1. No Silent Clobber** | NEVER overwrite vanilla game binaries (`.exe`, `.pak`, `.bundle`, `.bsa`). | Protects game files from corruption; allows clean verification via Steam/Epic. |
| **2. Binary Version Gate** | Match `FileVersion` / `ProductVersion` of `.exe` with native hook DLLs. | Prevents silent memory address misalignment crashes on game boot. |
| **3. Staging Isolation** | Extract untrusted archives to `~/.gemini/staging/`, never direct to game root. | Prevents messy partial extractions and allows inspecting FOMOD XMLs. |
| **4. Transactional Manifest** | Record relative paths and SHA-256 hashes in `.gemi_mods/<mod>/manifest.json`. | Enables atomic rollback if installation encounters errors midway. |
| **5. Non-Destructive Patch** | Never modify installed mod source files in-place; create higher-priority override patches. | Allows updating mods without losing user customizations and tuning. |

---

## 2. Deterministic CLI Execution (`game_mod_tool.py`)

Gemi utilizes `<HOME>/.gemini/scripts/game_mod_tool.py` as the sensory-motor engine for modding:

### Command Matrix
```bash
# 1. Discover all installed Steam and Epic games on User's workstation
python <HOME>/.gemini/scripts/game_mod_tool.py discover

# 2. Inspect game executable version, detect mod frameworks (RED4ext, SKSE, BepInEx, etc.)
python <HOME>/.gemini/scripts/game_mod_tool.py inspect "<game_path>"

# 3. Validate Nexus Mods Personal API Key
python <HOME>/.gemini/scripts/game_mod_tool.py validate-key "<API_KEY>"

# 4. Deploy staged mod files with transactional manifest
python <HOME>/.gemini/scripts/game_mod_tool.py deploy "<staging_path>" "<game_path>" --name "<mod_name>"

# 5. Undeploy mod cleanly (reverting unmodified files, backing up user edits)
python <HOME>/.gemini/scripts/game_mod_tool.py undeploy "<game_path>" "<mod_name>"
```

---

## 3. Mod Acquisition Protocol

### 3.1. Nexus Mods API
- Nexus Mods REST API (v1) and GraphQL (v2) require a **Personal API Key**.
- Direct API download links (`/download_link.json`) are officially supported on **Nexus Premium** accounts.
- **For Free Accounts**: Download via browser or `nxm://` URL handler into `D:\Game Mentah\` or `<HOME>\Downloads\`, then hand off the file path to Gemi for automated staging, dependency checking, and deployment.

### 3.2. GitHub Open-Source Frameworks
- Core script engines and hook loaders (e.g., RED4ext, redscript, ArchiveXL, Codeware, Mod Settings, SKSE, BepInEx) should be fetched directly from official GitHub releases to ensure 100% binary matching with the user's game patch.

---

## 4. In-Game Live Editing & Hot-Reload Protocol

When requested to adjust game values, stats, or visuals during gameplay:
1. **Bethesda Creation Engine**: Generate non-destructive record overrides using Mutagen.
2. **Unity Games**: Hot-reload properties via BepInEx Harmony patches or local IPC socket.
3. **Unreal Engine 4/5**: Adjust live actors and dump schemas using RE-UE4SS Lua bridge.
4. **REDengine (Cyberpunk 2077)**: Configure dynamically via `Mod Settings` menu or `.reds` observers without quitting the game.
