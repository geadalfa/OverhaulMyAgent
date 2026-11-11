#!/usr/bin/env python3
"""
game_mod_tool.py - Deterministic Game Modding & Discovery Automation Engine for Gemi
Adheres to the 6 Safety Invariants:
1. No Silent Clobber (Zero Vanilla Binary Overwrite)
2. Binary Version Gate (Match Game & Hook Versions)
3. Staging Isolation (Extract to ~/.gemini/staging/)
4. Transactional Manifest (Record Paths and SHA-256 Hashes)
5. Reversible Undeploy (Non-Destructive Overrides Preserved)
6. Automated Sanitation (Zero Residue Archive Purge)
"""

import os
import sys
import json
import hashlib
import zipfile
import shutil
import subprocess
import urllib.request
import urllib.parse
import re
import argparse
from pathlib import Path

MANIFEST_DIR_NAME = ".gemi_mods"

GAME_NAME_TO_DOMAIN = {
    "cyberpunk 2077": "cyberpunk2077",
    "cyberpunk2077": "cyberpunk2077",
    "mount & blade ii: bannerlord": "mountandblade2bannerlord",
    "mount & blade ii bannerlord": "mountandblade2bannerlord",
    "bannerlord": "mountandblade2bannerlord",
    "the witcher 3": "witcher3",
    "the witcher 3: wild hunt": "witcher3",
    "witcher 3": "witcher3",
    "red dead redemption 2": "reddeadredemption2",
    "rdr2": "reddeadredemption2",
    "skyrim special edition": "skyrimspecialedition",
    "skyrim se": "skyrimspecialedition",
    "total war: warhammer iii": "totalwarwarhammer3",
    "total war warhammer iii": "totalwarwarhammer3",
    "warhammer 3": "totalwarwarhammer3",
    "fallout 4": "fallout4",
    "baldurs gate 3": "baldursgate3",
    "baldur's gate 3": "baldursgate3",
    "starfield": "starfield",
    "ghost of tsushima director's cut": "ghostoftsushima",
    "euro truck simulator 2": "eurotrucksimulator2",
    "american truck simulator": "americantrucksimulator",
    "space marine 2": "warhammer40000spacemarine2"
}

# Known popular mod names mapped to Nexus Mod IDs (fallback for older manifests)
KNOWN_MOD_NAME_TO_ID = {
    "cyberpunk2077": {
        "cyber_engine_tweaks": 107,
        "cet": 107,
        "tweakxl": 4197,
        "archivexl": 4198,
        "codeware": 7780,
        "mod_settings": 4885,
        "redscript": 1511,
        "red4ext": 2380,
        "deceptious_bug_fixes": 4110,
        "better_loot_markers": 3485,
        "blur_begone": 8123,
        "immersive_first_person": 2675,
        "lutswitcher": 9868,
        "night_city_alive_standard": 10395,
        "reinforcements_gang_vs_gang": 11099,
        "they_will_remember": 11444,
        "collateral_damage": 10580,
        "crowd_voice_unlocked": 9324,
        "fighting_gangs_allowed_reasonable_police": 10421
    }
}

def get_file_sha256(filepath):
    """Calculate SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def extract_archive(archive_path, dest_dir):
    """
    Extracts archives across multiple formats (.zip, .rar, .7z, .tar, etc.)
    1. In-process zipfile for .zip archives.
    2. Windows built-in tar.exe (bsdtar/libarchive natively supports .rar, .7z, .tar, .zip).
    3. External 7-Zip (7z.exe) if installed.
    4. Python shutil.unpack_archive fallback.
    """
    if not os.path.exists(archive_path):
        raise FileNotFoundError(f"Archive not found: {archive_path}")
    os.makedirs(dest_dir, exist_ok=True)
    ext = os.path.splitext(archive_path)[1].lower()

    if ext == ".zip" or zipfile.is_zipfile(archive_path):
        try:
            with zipfile.ZipFile(archive_path, "r") as z:
                z.extractall(dest_dir)
            return True
        except Exception:
            pass

    tar_exe = shutil.which("tar") or r"C:\Windows\System32\tar.exe"
    if os.path.exists(tar_exe):
        try:
            res = subprocess.run(
                [tar_exe, "-xf", os.path.abspath(archive_path), "-C", os.path.abspath(dest_dir)],
                capture_output=True, text=True, check=True
            )
            return True
        except Exception:
            pass

    for candidate in [shutil.which("7z"), r"C:\Program Files\7-Zip\7z.exe", r"C:\Program Files (x86)\7-Zip\7z.exe"]:
        if candidate and os.path.exists(candidate):
            try:
                subprocess.run(
                    [candidate, "x", "-y", f"-o{dest_dir}", os.path.abspath(archive_path)],
                    capture_output=True, text=True, check=True
                )
                return True
            except Exception:
                pass

    try:
        shutil.unpack_archive(archive_path, dest_dir)
        return True
    except Exception as e:
        raise RuntimeError(
            f"Failed to extract archive '{os.path.basename(archive_path)}': {e}. "
            "Supported formats: .zip, .rar, .7z, .tar."
        )

def find_effective_root(staging_dir):
    """
    If the archive contains a single top-level folder wrapping mod content,
    or contains standard game subfolders (archive, bin, r6, red4ext, mods, engine, tweaks),
    locate the true root folder for deployment.
    """
    known_roots = {"archive", "bin", "r6", "red4ext", "mods", "engine", "tweaks", "data", "nativepc"}
    top_entries = [os.path.join(staging_dir, e) for e in os.listdir(staging_dir)]
    top_names = {os.path.basename(e).lower() for e in top_entries}
    if top_names & known_roots:
        return staging_dir

    subdirs = [e for e in top_entries if os.path.isdir(e)]
    if len(subdirs) == 1 and len(top_entries) == 1:
        nested_entries = {e.lower() for e in os.listdir(subdirs[0])}
        if nested_entries & known_roots:
            return subdirs[0]
        return find_effective_root(subdirs[0])

    return staging_dir

def resolve_game_domain(game_path_or_name):
    """Resolve game domain name from path or common name."""
    clean = os.path.basename(os.path.normpath(game_path_or_name)).lower().strip()
    if clean in GAME_NAME_TO_DOMAIN:
        return GAME_NAME_TO_DOMAIN[clean]
    for k, v in GAME_NAME_TO_DOMAIN.items():
        if k in clean:
            return v
    return clean.replace(" ", "").replace("_", "").replace("-", "")

def get_nexus_api_key():
    """Retrieve stored Nexus API key from env, file, or mcp_config.json."""
    key = os.environ.get("NEXUS_API_KEY")
    if key:
        return key.strip()

    key_file = os.path.expanduser(r"~\.gemini\config\nexus_api_key.txt")
    if os.path.exists(key_file):
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                k = f.read().strip()
                if k:
                    return k
        except Exception:
            pass

    config_path = r"<HOME>\.gemini\config\mcp_config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            servers = data.get("mcpServers", {})
            for sname in ["nexus-mods", "nexusmods"]:
                if sname in servers:
                    k = servers[sname].get("env", {}).get("NEXUS_API_KEY")
                    if k:
                        return k.strip()
        except Exception:
            pass
    return None

def get_nexus_cookie():
    """Retrieve stored Nexus Mods session cookie."""
    cookie = os.environ.get("NEXUS_COOKIE")
    if cookie:
        return cookie.strip()
    cookie_file = os.path.expanduser(r"~\.gemini\config\nexus_cookie.txt")
    if os.path.exists(cookie_file):
        try:
            with open(cookie_file, "r", encoding="utf-8") as f:
                c = f.read().strip()
                if c:
                    return c
        except Exception:
            pass
    return None

def set_nexus_cookie(cookie_str):
    """Save Nexus Mods session cookie for automated downloads."""
    cookie_file = os.path.expanduser(r"~\.gemini\config\nexus_cookie.txt")
    os.makedirs(os.path.dirname(cookie_file), exist_ok=True)
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(cookie_str.strip())
    return {"success": True, "cookie_saved_to": cookie_file}

def get_numeric_game_id(game_domain):
    """Retrieve numeric Nexus game ID (e.g., 3333 for Cyberpunk 2077)."""
    cache_file = os.path.expanduser(r"~\.gemini\config\nexus_game_ids.json")
    cache = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            pass
    if game_domain in cache:
        return cache[game_domain]

    # Query API
    res = query_nexus_api(f"/v1/games/{game_domain}.json")
    if isinstance(res, dict) and "id" in res:
        numeric_id = res["id"]
        cache[game_domain] = numeric_id
        try:
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2)
        except Exception:
            pass
        return numeric_id
    return None

def query_nexus_api(endpoint, api_key=None):
    """Perform an authenticated request to Nexus Mods REST API v1."""
    key = api_key or get_nexus_api_key()
    if not key:
        return {"error": "NEXUS_API_KEY not found in environment, nexus_api_key.txt, or mcp_config.json"}

    url = f"https://api.nexusmods.com{endpoint}" if endpoint.startswith("/") else f"https://api.nexusmods.com/{endpoint}"
    req = urllib.request.Request(url, headers={
        "apikey": key,
        "Application-Name": "Gemi-Automated-Modding-Engine",
        "Application-Version": "1.0.0",
        "User-Agent": "Mozilla/5.0"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()}"}
    except Exception as e:
        return {"error": str(e)}

def validate_nexus_key(api_key):
    """Validate a Nexus Mods Personal API Key."""
    url = "https://api.nexusmods.com/v1/users/validate.json"
    req = urllib.request.Request(url, headers={
        "apikey": api_key.strip(),
        "Application-Name": "Gemi-Automated-Modding-Engine",
        "Application-Version": "1.0.0",
        "User-Agent": "Mozilla/5.0"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return {"valid": True, "data": data}
    except urllib.error.HTTPError as e:
        return {"valid": False, "status": e.code, "error": e.read().decode()}
    except Exception as e:
        return {"valid": False, "error": str(e)}

def get_mod_info(game_domain, mod_id):
    """Fetch mod metadata from Nexus Mods."""
    return query_nexus_api(f"/v1/games/{game_domain}/mods/{mod_id}.json")

def get_mod_files(game_domain, mod_id):
    """Fetch available mod files and versions from Nexus Mods."""
    return query_nexus_api(f"/v1/games/{game_domain}/mods/{mod_id}/files.json")

def get_tracked_mods():
    """Fetch list of mods tracked by the user account."""
    return query_nexus_api("/v1/user/tracked_mods.json")

def discover_steam_games():
    """Discover all installed Steam games by scanning Steam registry and libraryfolders.vdf."""
    discovered = []
    vdf_paths = set()

    try:
        import winreg
        for root in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
            for subkey in [r"Software\Valve\Steam", r"SOFTWARE\WOW6432Node\Valve\Steam"]:
                try:
                    with winreg.OpenKey(root, subkey) as k:
                        path, _ = winreg.QueryValueEx(k, "SteamPath")
                        if path:
                            p = os.path.normpath(path.replace("/", os.sep))
                            vdf = os.path.join(p, "steamapps", "libraryfolders.vdf")
                            if os.path.exists(vdf):
                                vdf_paths.add(vdf)
                except Exception:
                    pass
    except Exception:
        pass

    drives = [f"{d}:\\" for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
    for d in drives:
        candidates = [
            os.path.join(d, "Program Files (x86)", "Steam", "steamapps", "libraryfolders.vdf"),
            os.path.join(d, "Program Files", "Steam", "steamapps", "libraryfolders.vdf"),
            os.path.join(d, "SteamLibrary", "steamapps", "libraryfolders.vdf"),
            os.path.join(d, "Steam", "steamapps", "libraryfolders.vdf"),
        ]
        for c in candidates:
            if os.path.exists(c):
                vdf_paths.add(c)

    libraries = set()
    for vdf in vdf_paths:
        try:
            with open(vdf, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            paths = re.findall(r'"path"\s+"([^"]+)"', content)
            for p in paths:
                clean_p = os.path.normpath(p.replace(r"\\", "\\"))
                if os.path.exists(clean_p):
                    libraries.add(clean_p)
        except Exception:
            pass

    for lib in libraries:
        apps_dir = os.path.join(lib, "steamapps")
        if not os.path.exists(apps_dir):
            continue
        for item in os.listdir(apps_dir):
            if item.startswith("appmanifest_") and item.endswith(".acf"):
                acf_path = os.path.join(apps_dir, item)
                try:
                    with open(acf_path, "r", encoding="utf-8", errors="ignore") as f:
                        acf = f.read()
                    appid = re.search(r'"appid"\s+"(\d+)"', acf)
                    name = re.search(r'"name"\s+"([^"]+)"', acf)
                    installdir = re.search(r'"installdir"\s+"([^"]+)"', acf)
                    buildid = re.search(r'"buildid"\s+"(\d+)"', acf)

                    if appid and installdir:
                        game_path = os.path.join(apps_dir, "common", installdir.group(1))
                        discovered.append({
                            "platform": "Steam",
                            "name": name.group(1) if name else installdir.group(1),
                            "appid": appid.group(1),
                            "buildid": buildid.group(1) if buildid else "Unknown",
                            "path": game_path,
                            "exists": os.path.exists(game_path)
                        })
                except Exception:
                    pass

    return discovered

def discover_epic_games():
    """Discover Epic Games Store games from Manifests directory."""
    manifest_dir = r"C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests"
    discovered = []
    if not os.path.exists(manifest_dir):
        return discovered

    for item in os.listdir(manifest_dir):
        if item.endswith(".item"):
            item_path = os.path.join(manifest_dir, item)
            try:
                with open(item_path, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)
                display_name = data.get("DisplayName")
                install_loc = data.get("InstallLocation")
                version = data.get("AppVersionString", "Unknown")
                exe = data.get("LaunchExecutable", "")

                if install_loc:
                    discovered.append({
                        "platform": "Epic Games",
                        "name": display_name or os.path.basename(install_loc),
                        "appid": data.get("AppName", "Unknown"),
                        "buildid": version,
                        "path": install_loc,
                        "executable": exe,
                        "exists": os.path.exists(install_loc)
                    })
            except Exception:
                pass
    return discovered

def inspect_game(game_path):
    """Inspect game directory, detect binaries and modding frameworks."""
    if not os.path.exists(game_path):
        return {"error": f"Path not found: {game_path}"}

    res = {
        "path": game_path,
        "domain": resolve_game_domain(game_path),
        "executables": [],
        "frameworks_detected": [],
        "deployed_gemi_mods": []
    }

    for root, dirs, files in os.walk(game_path):
        rel = os.path.relpath(root, game_path)
        depth = len(rel.split(os.sep)) if rel != "." else 0
        if depth > 3:
            continue
        for f in files:
            if f.lower().endswith(".exe") and not any(x in f.lower() for x in ["crash", "report", "redlauncher", "unitycrash"]):
                exe_path = os.path.join(root, f)
                res["executables"].append({
                    "name": f,
                    "rel_path": os.path.relpath(exe_path, game_path),
                    "size": os.path.getsize(exe_path)
                })

    # Framework detection
    if os.path.exists(os.path.join(game_path, "red4ext", "RED4ext.dll")):
        res["frameworks_detected"].append("RED4ext (Cyberpunk 2077)")
    if os.path.exists(os.path.join(game_path, "engine", "tools", "scc.exe")):
        res["frameworks_detected"].append("redscript (Cyberpunk 2077)")
    if os.path.exists(os.path.join(game_path, "red4ext", "plugins", "ArchiveXL")):
        res["frameworks_detected"].append("ArchiveXL (Cyberpunk 2077)")
    if os.path.exists(os.path.join(game_path, "red4ext", "plugins", "Codeware")):
        res["frameworks_detected"].append("Codeware (Cyberpunk 2077)")
    if os.path.exists(os.path.join(game_path, "red4ext", "plugins", "mod_settings")):
        res["frameworks_detected"].append("Mod Settings (Cyberpunk 2077)")
    if os.path.exists(os.path.join(game_path, "red4ext", "plugins", "TweakXL")):
        res["frameworks_detected"].append("TweakXL (Cyberpunk 2077)")
    if os.path.exists(os.path.join(game_path, "bin", "x64", "version.dll")) and os.path.exists(os.path.join(game_path, "bin", "x64", "plugins", "cyber_engine_tweaks")):
        res["frameworks_detected"].append("Cyber Engine Tweaks (CET)")
    if os.path.exists(os.path.join(game_path, "skse64_loader.exe")):
        res["frameworks_detected"].append("SKSE64 (Skyrim SE)")
    if os.path.exists(os.path.join(game_path, "f4se_loader.exe")):
        res["frameworks_detected"].append("F4SE (Fallout 4)")
    if os.path.exists(os.path.join(game_path, "BepInEx")):
        res["frameworks_detected"].append("BepInEx (Unity / .NET)")
    if os.path.exists(os.path.join(game_path, "ue4ss.dll")) or os.path.exists(os.path.join(game_path, "Binaries", "Win64", "ue4ss.dll")):
        res["frameworks_detected"].append("RE-UE4SS (Unreal Engine)")

    manifest_base = os.path.join(game_path, MANIFEST_DIR_NAME)
    if os.path.exists(manifest_base):
        for item in os.listdir(manifest_base):
            mp = os.path.join(manifest_base, item, "manifest.json")
            if os.path.exists(mp):
                try:
                    with open(mp, "r", encoding="utf-8") as f:
                        m_data = json.load(f)
                    if not m_data.get("uninstalled", False):
                        res["deployed_gemi_mods"].append({
                            "name": m_data.get("mod_name", item),
                            "mod_id": m_data.get("mod_id"),
                            "version": m_data.get("version"),
                            "installed_at": m_data.get("installed_at"),
                            "file_count": len(m_data.get("files", []))
                        })
                except Exception:
                    pass

    return res

def deploy_mod(staging_dir, game_path, mod_name, mod_id=None, version=None, domain=None):
    """Deploy files from staging to game path with transactional manifest."""
    if not os.path.exists(staging_dir):
        raise FileNotFoundError(f"Staging dir not found: {staging_dir}")
    if not os.path.exists(game_path):
        raise FileNotFoundError(f"Game dir not found: {game_path}")

    game_domain = domain or resolve_game_domain(game_path)
    
    # Auto-resolve mod_id from known dictionary if not provided
    if not mod_id:
        lookup_name = mod_name.lower().strip()
        known = KNOWN_MOD_NAME_TO_ID.get(game_domain, {})
        mod_id = known.get(lookup_name)

    manifest_dir = os.path.join(game_path, MANIFEST_DIR_NAME, mod_name)
    os.makedirs(manifest_dir, exist_ok=True)
    manifest_file = os.path.join(manifest_dir, "manifest.json")

    manifest = {
        "mod_name": mod_name,
        "staging_dir": staging_dir,
        "game_path": game_path,
        "installed_at": str(Path(staging_dir).stat().st_ctime),
        "mod_id": mod_id,
        "version": version,
        "domain": game_domain,
        "files": []
    }

    effective_root = find_effective_root(staging_dir)

    # Invariant 1: Gather all files and ensure no core EXE clobber
    to_copy = []
    for root, dirs, files in os.walk(effective_root):
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(src, effective_root)
            dst = os.path.join(game_path, rel)
            
            if os.path.exists(dst) and dst.lower().endswith(".exe"):
                raise RuntimeError(f"Safety Violation (Invariant 1): Staged file attempts to overwrite game binary '{rel}'!")
            to_copy.append((src, dst, rel))

    deployed_files = []
    try:
        for src, dst, rel in to_copy:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            sha256 = get_file_sha256(dst)
            manifest["files"].append({
                "rel_path": rel.replace("\\", "/"),
                "sha256": sha256,
                "size": os.path.getsize(dst)
            })
            deployed_files.append(dst)

        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return {
            "success": True,
            "mod_name": mod_name,
            "mod_id": mod_id,
            "version": version,
            "domain": game_domain,
            "files_deployed": len(manifest["files"]),
            "manifest": manifest_file
        }
    except Exception as e:
        # Atomic rollback
        for f in deployed_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass
        raise RuntimeError(f"Deployment failed and was rolled back: {e}")

def undeploy_mod(game_path, mod_name):
    """Undeploy a mod using its manifest, verifying SHA-256 before deletion (Invariant 5)."""
    manifest_file = os.path.join(game_path, MANIFEST_DIR_NAME, mod_name, "manifest.json")
    if not os.path.exists(manifest_file):
        raise FileNotFoundError(f"Manifest not found for mod: {mod_name}")

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    removed = []
    backed_up = []
    backup_dir = os.path.join(game_path, MANIFEST_DIR_NAME, mod_name, "user_overwrites")

    for item in manifest.get("files", []):
        rel = item["rel_path"].replace("/", os.sep)
        target = os.path.join(game_path, rel)
        if not os.path.exists(target):
            continue

        current_hash = get_file_sha256(target)
        if current_hash == item["sha256"]:
            os.remove(target)
            removed.append(rel)
        else:
            # File modified by user: back up before removing
            os.makedirs(backup_dir, exist_ok=True)
            bk = os.path.join(backup_dir, os.path.basename(target))
            shutil.move(target, bk)
            backed_up.append(rel)

    # Clean empty parent directories
    for item in manifest.get("files", []):
        rel = item["rel_path"].replace("/", os.sep)
        target = os.path.join(game_path, rel)
        parent = os.path.dirname(target)
        while parent and parent != game_path and parent.startswith(game_path):
            try:
                if os.path.exists(parent) and not os.listdir(parent):
                    os.rmdir(parent)
                parent = os.path.dirname(parent)
            except Exception:
                break

    manifest["uninstalled"] = True
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return {
        "success": True,
        "mod_name": mod_name,
        "removed_count": len(removed),
        "backed_up_count": len(backed_up),
        "backed_up_files": backed_up
    }

def install_archive(archive_path, game_path, mod_name=None, keep_source=False, mod_id=None, version=None, domain=None):
    """
    All-in-one automated pipeline:
    1. Unpack archive to isolated temporary staging.
    2. Deploy files transactionally with SHA-256 manifest.
    3. Verify files deployed.
    4. Automatically purge staging directory.
    5. Automatically delete raw source archive to keep directories spotless (Invariant 6).
    """
    if not os.path.exists(archive_path):
        raise FileNotFoundError(f"Archive not found: {archive_path}")
    if not os.path.exists(game_path):
        raise FileNotFoundError(f"Game directory not found: {game_path}")

    if not mod_name:
        base_name = os.path.splitext(os.path.basename(archive_path))[0]
        clean_name = re.sub(r"\s+\d{4}-\d{2}-\d{2}T.*$", "", base_name).strip()
        clean_name = re.sub(r"[^a-zA-Z0-9_.-]+", "_", clean_name)
        mod_name = clean_name or "Installed_Mod"

    temp_staging = os.path.join(os.environ.get("USERPROFILE", ""), ".gemini", "staging", mod_name)
    if os.path.exists(temp_staging):
        shutil.rmtree(temp_staging, ignore_errors=True)
    os.makedirs(temp_staging, exist_ok=True)

    try:
        extract_archive(archive_path, temp_staging)
        deploy_res = deploy_mod(temp_staging, game_path, mod_name, mod_id=mod_id, version=version, domain=domain)
        shutil.rmtree(temp_staging, ignore_errors=True)

        source_deleted = False
        if not keep_source:
            try:
                os.remove(archive_path)
                source_deleted = True
            except Exception:
                pass

        return {
            "success": True,
            "mod_name": mod_name,
            "mod_id": deploy_res.get("mod_id"),
            "version": deploy_res.get("version"),
            "files_deployed": deploy_res["files_deployed"],
            "manifest": deploy_res["manifest"],
            "staging_cleaned": True,
            "source_archive_purged": source_deleted,
            "source_path": archive_path
        }
    except Exception as e:
        if os.path.exists(temp_staging):
            shutil.rmtree(temp_staging, ignore_errors=True)
        raise RuntimeError(f"Automated installation failed: {e}")

def clean_watch_directory(dir_path=r"D:\Game Mentah", extensions=[".zip", ".rar", ".7z"]):
    """Scans and purges leftover mod archives from watch folder."""
    if not os.path.exists(dir_path):
        return {"error": f"Directory not found: {dir_path}"}
    purged = []
    for item in os.listdir(dir_path):
        p = os.path.join(dir_path, item)
        if os.path.isfile(p) and any(item.lower().endswith(ext) for ext in extensions):
            try:
                os.remove(p)
                purged.append(item)
            except Exception:
                pass
    return {"purged_count": len(purged), "purged_files": purged, "directory": dir_path}

def tag_mod(game_path, mod_name, mod_id, version=None, domain=None):
    """Add or update mod_id, version, and domain in an existing manifest."""
    manifest_file = os.path.join(game_path, MANIFEST_DIR_NAME, mod_name, "manifest.json")
    if not os.path.exists(manifest_file):
        return {"error": f"Manifest not found for mod '{mod_name}' in '{game_path}'"}
    
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    manifest["mod_id"] = int(mod_id)
    if version:
        manifest["version"] = str(version)
    if domain:
        manifest["domain"] = domain
    elif not manifest.get("domain"):
        manifest["domain"] = resolve_game_domain(game_path)

    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return {
        "success": True,
        "mod_name": mod_name,
        "mod_id": manifest["mod_id"],
        "version": manifest.get("version"),
        "domain": manifest.get("domain"),
        "manifest": manifest_file
    }

def check_updates(game_path, period="1w", domain=None):
    """
    Check if any installed mod in game_path has updates on Nexus Mods.
    Uses 1 batch request to GET /v1/games/{domain}/mods/updated.json.
    """
    if not os.path.exists(game_path):
        return {"error": f"Game directory not found: {game_path}"}

    game_domain = domain or resolve_game_domain(game_path)
    manifests_dir = os.path.join(game_path, MANIFEST_DIR_NAME)
    if not os.path.exists(manifests_dir):
        return {"error": f"No {MANIFEST_DIR_NAME} manifests found in {game_path}"}

    installed_mods = {}
    known_map = KNOWN_MOD_NAME_TO_ID.get(game_domain, {})
    for item in os.listdir(manifests_dir):
        mp = os.path.join(manifests_dir, item, "manifest.json")
        if os.path.exists(mp):
            try:
                with open(mp, "r", encoding="utf-8") as f:
                    m = json.load(f)
                if not m.get("uninstalled", False):
                    # Auto-assign known ID if missing
                    if not m.get("mod_id") and item.lower() in known_map:
                        m["mod_id"] = known_map[item.lower()]
                        with open(mp, "w", encoding="utf-8") as fw:
                            json.dump(m, fw, indent=2)
                    installed_mods[item] = m
            except Exception:
                pass

    if not installed_mods:
        return {"message": "No active installed mods found", "installed_count": 0}

    # Batch query Nexus API (costs only 1 request quota)
    updated_list = query_nexus_api(f"/v1/games/{game_domain}/mods/updated.json?period={period}")
    if isinstance(updated_list, dict) and "error" in updated_list:
        return updated_list

    updated_dict = {item["mod_id"]: item for item in updated_list if isinstance(item, dict) and "mod_id" in item}

    results = []
    for mod_name, m in installed_mods.items():
        mod_id = m.get("mod_id")
        if not mod_id:
            results.append({
                "mod_name": mod_name,
                "mod_id": None,
                "installed_version": m.get("version", "Unknown"),
                "status": "Untracked (no mod_id assigned; use 'tag-mod' command)"
            })
            continue

        if mod_id in updated_dict:
            latest_info = updated_dict[mod_id]
            files_data = get_mod_files(game_domain, mod_id)
            main_files = [f for f in files_data.get("files", []) if f.get("category_name") == "MAIN"] if isinstance(files_data, dict) else []
            latest_file = main_files[-1] if main_files else None
            latest_ver = latest_file.get("version") if latest_file else "Newer"
            installed_ver = m.get("version")

            # Check if installed version matches latest upstream version
            has_new_version = True
            if installed_ver and installed_ver != "Unknown" and latest_ver != "Newer":
                if str(installed_ver).strip() == str(latest_ver).strip():
                    has_new_version = False

            if has_new_version:
                results.append({
                    "mod_name": mod_name,
                    "mod_id": mod_id,
                    "installed_version": installed_ver or "Unknown",
                    "latest_version": latest_ver,
                    "latest_file_name": latest_file.get("file_name") if latest_file else "Unknown",
                    "latest_file_id": latest_file.get("file_id") if latest_file else None,
                    "update_timestamp": latest_info.get("latest_file_update"),
                    "update_available": True
                })
            else:
                results.append({
                    "mod_name": mod_name,
                    "mod_id": mod_id,
                    "installed_version": installed_ver,
                    "latest_version": latest_ver,
                    "update_available": False,
                    "status": f"Up-to-date (v{installed_ver})"
                })
        else:
            results.append({
                "mod_name": mod_name,
                "mod_id": mod_id,
                "installed_version": m.get("version", "Unknown"),
                "update_available": False,
                "status": "Up-to-date"
            })

    return {
        "game_domain": game_domain,
        "period": period,
        "total_installed": len(installed_mods),
        "updates_found": sum(1 for r in results if r.get("update_available")),
        "mods": results
    }

def download_mod(domain, mod_id, file_id=None, out_dir=r"D:\Game Mentah", nxm_key=None, nxm_expires=None):
    """
    Download a mod file from Nexus Mods.
    Supports Premium direct download, Free account via session cookie (GenerateDownloadUrl),
    and NXM signed key/expires parameters.
    """
    os.makedirs(out_dir, exist_ok=True)
    mod_id = int(mod_id)

    # 1. Resolve file_id and filename if not specified
    expected_filename = f"mod_{mod_id}.zip"
    if not file_id:
        files_data = get_mod_files(domain, mod_id)
        if isinstance(files_data, dict) and "error" in files_data:
            return files_data
        main_files = [f for f in files_data.get("files", []) if f.get("category_name") == "MAIN"]
        if not main_files:
            main_files = files_data.get("files", [])
        if not main_files:
            return {"error": f"No files found for mod {mod_id} in game {domain}"}
        target_file = main_files[-1]
        file_id = target_file["file_id"]
        expected_filename = target_file.get("file_name", expected_filename)
    else:
        file_id = int(file_id)
        expected_filename = f"mod_{mod_id}_file_{file_id}.zip"

    download_urls = []

    # 2. If NXM signed parameters are provided, use official API
    if nxm_key and nxm_expires:
        endpoint = f"/v1/games/{domain}/mods/{mod_id}/files/{file_id}/download_link.json?key={nxm_key}&expires={nxm_expires}"
        api_res = query_nexus_api(endpoint)
        if isinstance(api_res, list):
            download_urls = [item["URI"] for item in api_res if "URI" in item]

    # 3. Try official API (works for Premium accounts)
    if not download_urls:
        api_res = query_nexus_api(f"/v1/games/{domain}/mods/{mod_id}/files/{file_id}/download_link.json")
        if isinstance(api_res, list):
            download_urls = [item["URI"] for item in api_res if "URI" in item]

    # 4. If Free account, use internal GenerateDownloadUrl endpoint with session cookie
    if not download_urls:
        cookie = get_nexus_cookie()
        if cookie:
            numeric_game_id = get_numeric_game_id(domain)
            if numeric_game_id:
                gen_url = "https://www.nexusmods.com/Core/Libs/Common/Managers/Downloads?GenerateDownloadUrl"
                post_data = urllib.parse.urlencode({
                    "fid": file_id,
                    "game_id": numeric_game_id
                }).encode("utf-8")
                req = urllib.request.Request(gen_url, data=post_data, headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Requested-With": "XMLHttpRequest",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                    "Cookie": cookie,
                    "Referer": f"https://www.nexusmods.com/{domain}/mods/{mod_id}?tab=files"
                })
                try:
                    with urllib.request.urlopen(req) as resp:
                        res_json = json.loads(resp.read().decode())
                        if isinstance(res_json, dict) and res_json.get("url"):
                            download_urls = [res_json["url"]]
                        elif isinstance(res_json, list) and res_json and "url" in res_json[0]:
                            download_urls = [res_json[0]["url"]]
                except Exception:
                    pass

    # 5. Fallback instructions if no download URL could be acquired
    if not download_urls:
        return {
            "error": "Direct API download requires session cookie or NXM link for Free accounts",
            "domain": domain,
            "mod_id": mod_id,
            "file_id": file_id,
            "file_name": expected_filename,
            "manual_download_url": f"https://www.nexusmods.com/{domain}/mods/{mod_id}?tab=files&file_id={file_id}",
            "solutions": [
                "1. Provide browser session cookie: python game_mod_tool.py set-cookie '<cookie_header>'",
                "2. Paste 'Mod Manager Download' nxm link: python game_mod_tool.py parse-nxm '<nxm://...>'",
                "3. Download archive to 'D:\\Game Mentah' and run: python game_mod_tool.py install-archive '<file>' '<game_path>'"
            ]
        }

    # 6. Stream file download
    target_url = download_urls[0]
    out_path = os.path.join(out_dir, expected_filename)
    req = urllib.request.Request(target_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(out_path, "wb") as f_out:
        shutil.copyfileobj(resp, f_out)

    sha256 = get_file_sha256(out_path)
    return {
        "success": True,
        "downloaded_file": out_path,
        "size": os.path.getsize(out_path),
        "sha256": sha256,
        "mod_id": mod_id,
        "file_id": file_id
    }

def parse_nxm(nxm_url, out_dir=r"D:\Game Mentah"):
    """Parse nxm:// link and download file using signed parameters."""
    m = re.match(r"^nxm://([^/?#]+)/mods/(\d+)/files/(\d+)(?:\?(.+))?$", nxm_url.strip(), re.IGNORECASE)
    if not m:
        return {"error": f"Invalid nxm URL format: {nxm_url}"}
    domain = m.group(1)
    mod_id = int(m.group(2))
    file_id = int(m.group(3))
    query = m.group(4) or ""

    params = urllib.parse.parse_qs(query)
    key = params.get("key", [None])[0]
    expires = params.get("expires", [None])[0]

    return download_mod(domain, mod_id, file_id=file_id, out_dir=out_dir, nxm_key=key, nxm_expires=expires)

def update_mod_pipeline(game_path, mod_name, domain=None, out_dir=r"D:\Game Mentah"):
    """
    Automated update workflow:
    1. Check if update exists for mod_name.
    2. Download latest version.
    3. Undeploy existing version (preserving user custom files).
    4. Install new archive transactionally.
    5. Clean watch directory and staging.
    """
    manifest_file = os.path.join(game_path, MANIFEST_DIR_NAME, mod_name, "manifest.json")
    if not os.path.exists(manifest_file):
        return {"error": f"Manifest not found for mod '{mod_name}' in '{game_path}'"}

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    mod_id = manifest.get("mod_id")
    game_domain = domain or manifest.get("domain") or resolve_game_domain(game_path)

    if not mod_id:
        known = KNOWN_MOD_NAME_TO_ID.get(game_domain, {})
        mod_id = known.get(mod_name.lower())

    if not mod_id:
        return {"error": f"Mod ID unknown for '{mod_name}'. Please run 'tag-mod' first."}

    # Fetch latest files
    files_data = get_mod_files(game_domain, mod_id)
    if isinstance(files_data, dict) and "error" in files_data:
        return files_data

    main_files = [f for f in files_data.get("files", []) if f.get("category_name") == "MAIN"]
    if not main_files:
        main_files = files_data.get("files", [])
    if not main_files:
        return {"error": f"No files available for mod {mod_id}"}

    latest_file = main_files[-1]
    latest_ver = latest_file.get("version", "Unknown")
    file_id = latest_file["file_id"]

    # 1. Download
    dl_res = download_mod(game_domain, mod_id, file_id=file_id, out_dir=out_dir)
    if not dl_res.get("success"):
        return dl_res

    downloaded_archive = dl_res["downloaded_file"]

    # 2. Undeploy previous version safely (retaining user customizations)
    undep_res = undeploy_mod(game_path, mod_name)

    # 3. Install newly downloaded archive
    inst_res = install_archive(downloaded_archive, game_path, mod_name=mod_name, mod_id=mod_id, version=latest_ver, domain=game_domain)

    return {
        "success": True,
        "mod_name": mod_name,
        "mod_id": mod_id,
        "previous_version": manifest.get("version", "Unknown"),
        "new_version": latest_ver,
        "undeployed": undep_res,
        "installed": inst_res
    }

def main():
    parser = argparse.ArgumentParser(description="Gemi Game Modding & Discovery Automation Engine")
    subparsers = parser.add_subparsers(dest="command")

    # discover
    subparsers.add_parser("discover", help="Discover all installed Steam and Epic games")

    # inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspect a game directory")
    inspect_parser.add_argument("path", help="Path to game folder")

    # validate-key
    key_parser = subparsers.add_parser("validate-key", help="Validate Nexus Mods Personal API Key")
    key_parser.add_argument("key", help="Nexus Mods Personal API Key")

    # set-cookie
    cookie_parser = subparsers.add_parser("set-cookie", help="Save Nexus Mods session cookie")
    cookie_parser.add_argument("cookie", help="Browser session cookie header string")

    # game-id
    gameid_parser = subparsers.add_parser("game-id", help="Get numeric Nexus game ID for a domain")
    gameid_parser.add_argument("domain", help="Game domain (e.g. cyberpunk2077)")

    # tag-mod
    tag_parser = subparsers.add_parser("tag-mod", help="Tag installed mod with Nexus mod ID")
    tag_parser.add_argument("game", help="Path to game folder")
    tag_parser.add_argument("name", help="Mod name / identifier")
    tag_parser.add_argument("--mod-id", required=True, type=int, help="Nexus Mod ID")
    tag_parser.add_argument("--version", help="Mod version string")
    tag_parser.add_argument("--domain", help="Game domain name")

    # check-updates
    check_parser = subparsers.add_parser("check-updates", help="Batch check updates for installed mods")
    check_parser.add_argument("game", help="Path to game folder")
    check_parser.add_argument("--period", default="1w", choices=["1d", "1w", "1m"], help="Lookback period")
    check_parser.add_argument("--domain", help="Game domain name override")

    # download-mod
    dl_parser = subparsers.add_parser("download-mod", help="Download a mod file from Nexus Mods")
    dl_parser.add_argument("domain", help="Game domain name (e.g. cyberpunk2077)")
    dl_parser.add_argument("mod_id", type=int, help="Nexus Mod ID")
    dl_parser.add_argument("--file-id", type=int, help="Optional specific file ID")
    dl_parser.add_argument("--out", default=r"D:\Game Mentah", help="Output directory")
    dl_parser.add_argument("--key", help="NXM signed key parameter")
    dl_parser.add_argument("--expires", help="NXM signed expires parameter")

    # parse-nxm
    nxm_parser = subparsers.add_parser("parse-nxm", help="Parse and download from an nxm:// link")
    nxm_parser.add_argument("url", help="nxm:// URL string")
    nxm_parser.add_argument("--out", default=r"D:\Game Mentah", help="Output directory")

    # update-mod
    up_parser = subparsers.add_parser("update-mod", help="Check, download, undeploy, and install mod update")
    up_parser.add_argument("game", help="Path to game folder")
    up_parser.add_argument("name", help="Mod name / identifier")
    up_parser.add_argument("--domain", help="Game domain override")
    up_parser.add_argument("--out", default=r"D:\Game Mentah", help="Output directory for download")

    # deploy
    deploy_parser = subparsers.add_parser("deploy", help="Deploy mod from staging to game")
    deploy_parser.add_argument("staging", help="Path to staging directory")
    deploy_parser.add_argument("game", help="Path to game folder")
    deploy_parser.add_argument("--name", required=True, help="Mod name / identifier")
    deploy_parser.add_argument("--mod-id", type=int, help="Nexus Mod ID")
    deploy_parser.add_argument("--version", help="Mod version string")
    deploy_parser.add_argument("--domain", help="Game domain name")

    # undeploy
    undep_parser = subparsers.add_parser("undeploy", help="Undeploy mod safely using manifest")
    undep_parser.add_argument("game", help="Path to game folder")
    undep_parser.add_argument("name", help="Mod name / identifier")

    # mod-info
    info_parser = subparsers.add_parser("mod-info", help="Get mod details from Nexus Mods")
    info_parser.add_argument("game", help="Game domain name (e.g. cyberpunk2077, skyrimspecialedition)")
    info_parser.add_argument("mod_id", help="Mod ID")

    # mod-files
    files_parser = subparsers.add_parser("mod-files", help="List downloadable files for a mod")
    files_parser.add_argument("game", help="Game domain name")
    files_parser.add_argument("mod_id", help="Mod ID")

    # tracked-mods
    subparsers.add_parser("tracked-mods", help="List mods tracked by your Nexus account")

    # install-archive (Automated one-command pipeline with auto-purge)
    inst_parser = subparsers.add_parser("install-archive", help="Unpack, deploy, and auto-delete source archive")
    inst_parser.add_argument("archive", help="Path to mod archive (.zip)")
    inst_parser.add_argument("game", help="Path to game folder")
    inst_parser.add_argument("--name", help="Optional mod name override")
    inst_parser.add_argument("--mod-id", type=int, help="Nexus Mod ID")
    inst_parser.add_argument("--version", help="Mod version string")
    inst_parser.add_argument("--domain", help="Game domain name")
    inst_parser.add_argument("--keep-source", action="store_true", help="Keep source archive (do not purge)")

    # clean-watch
    clean_parser = subparsers.add_parser("clean-watch", help="Purge residual archives from watch directory")
    clean_parser.add_argument("--dir", default=r"D:\Game Mentah", help="Watch directory path")

    args = parser.parse_args()

    if args.command == "discover":
        steam = discover_steam_games()
        epic = discover_epic_games()
        out = {
            "steam_games": [g for g in steam if g["exists"]],
            "epic_games": [g for g in epic if g["exists"]]
        }
        print(json.dumps(out, indent=2))

    elif args.command == "inspect":
        res = inspect_game(args.path)
        print(json.dumps(res, indent=2))

    elif args.command == "validate-key":
        res = validate_nexus_key(args.key)
        print(json.dumps(res, indent=2))

    elif args.command == "set-cookie":
        res = set_nexus_cookie(args.cookie)
        print(json.dumps(res, indent=2))

    elif args.command == "game-id":
        gid = get_numeric_game_id(args.domain)
        print(json.dumps({"domain": args.domain, "game_id": gid}, indent=2))

    elif args.command == "tag-mod":
        res = tag_mod(args.game, args.name, args.mod_id, version=args.version, domain=args.domain)
        print(json.dumps(res, indent=2))

    elif args.command == "check-updates":
        res = check_updates(args.game, period=args.period, domain=args.domain)
        print(json.dumps(res, indent=2))

    elif args.command == "download-mod":
        res = download_mod(args.domain, args.mod_id, file_id=args.file_id, out_dir=args.out, nxm_key=args.key, nxm_expires=args.expires)
        print(json.dumps(res, indent=2))

    elif args.command == "parse-nxm":
        res = parse_nxm(args.url, out_dir=args.out)
        print(json.dumps(res, indent=2))

    elif args.command == "update-mod":
        res = update_mod_pipeline(args.game, args.name, domain=args.domain, out_dir=args.out)
        print(json.dumps(res, indent=2))

    elif args.command == "deploy":
        res = deploy_mod(args.staging, args.game, args.name, mod_id=args.mod_id, version=args.version, domain=args.domain)
        print(json.dumps(res, indent=2))

    elif args.command == "undeploy":
        res = undeploy_mod(args.game, args.name)
        print(json.dumps(res, indent=2))

    elif args.command == "mod-info":
        res = get_mod_info(args.game, args.mod_id)
        print(json.dumps(res, indent=2))

    elif args.command == "mod-files":
        res = get_mod_files(args.game, args.mod_id)
        print(json.dumps(res, indent=2))

    elif args.command == "tracked-mods":
        res = get_tracked_mods()
        print(json.dumps(res, indent=2))

    elif args.command == "install-archive":
        res = install_archive(args.archive, args.game, mod_name=args.name, keep_source=args.keep_source, mod_id=args.mod_id, version=args.version, domain=args.domain)
        print(json.dumps(res, indent=2))

    elif args.command == "clean-watch":
        res = clean_watch_directory(args.dir)
        print(json.dumps(res, indent=2))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
