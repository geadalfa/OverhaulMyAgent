#!/usr/bin/env python3
"""
OverhaulMyAgent - Unified Dual-Pipeline Export & Sync Engine.
Executes both Private Google Drive Cloud Backup AND Public Zero-PII GitHub Sync.
Runs cross-platform on macOS and Windows.
"""

import os
import sys
import io
import subprocess

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HOME = os.path.expanduser("~")
GEMINI_DIR = os.path.join(HOME, ".gemini")
SCRIPTS_DIR = os.path.join(GEMINI_DIR, "scripts")

EXPORT_BUNDLE_PY = os.path.join(GEMINI_DIR, "export_gemi_bundle.py")
EXPORT_CONFIG_SH = os.path.join(SCRIPTS_DIR, "export_gemi_config.sh")
SYNC_GITHUB_PY = os.path.join(SCRIPTS_DIR, "sync_overhaul_github.py")

CYAN = "\033[96m" if sys.platform != "win32" or "WT_SESSION" in os.environ else ""
GREEN = "\033[92m" if sys.platform != "win32" or "WT_SESSION" in os.environ else ""
YELLOW = "\033[93m" if sys.platform != "win32" or "WT_SESSION" in os.environ else ""
BOLD = "\033[1m" if sys.platform != "win32" or "WT_SESSION" in os.environ else ""
RESET = "\033[0m" if sys.platform != "win32" or "WT_SESSION" in os.environ else ""


def main():
    print(f"{BOLD}{CYAN}=================================================================={RESET}")
    print(f"{BOLD}{CYAN}  UNIFIED EXPORT: GOOGLE DRIVE BACKUP & GITHUB OVERHAUL SYNC     {RESET}")
    print(f"{BOLD}{CYAN}=================================================================={RESET}")
    print(f"Platform: {sys.platform.upper()} | User Home: {HOME}")

    # 1. Pipeline A: Google Drive Cloud Backup
    print(f"\n{BOLD}[1/2] Menyinkronkan Backup Lengkap ke Google Drive...{RESET}")
    gdrive_success = False
    if os.path.exists(EXPORT_BUNDLE_PY):
        print(f"  -> Menjalankan {os.path.basename(EXPORT_BUNDLE_PY)}...")
        res_gd = subprocess.run([sys.executable, EXPORT_BUNDLE_PY], capture_output=False)
        if res_gd.returncode == 0:
            gdrive_success = True
            print(f"  {GREEN}[✓] Backup Google Drive berhasil diperbarui.{RESET}")
        else:
            print(f"  {YELLOW}[!] export_gemi_bundle.py keluar dengan kode {res_gd.returncode}{RESET}")
    elif sys.platform == "darwin" and os.path.exists(EXPORT_CONFIG_SH):
        print(f"  -> Menjalankan {os.path.basename(EXPORT_CONFIG_SH)}...")
        res_sh = subprocess.run(["bash", EXPORT_CONFIG_SH], capture_output=False)
        if res_sh.returncode == 0:
            gdrive_success = True
            print(f"  {GREEN}[✓] Backup Google Drive berhasil diperbarui via Bash.{RESET}")

    # 2. Pipeline B: Public Zero-PII GitHub Sync (OverhaulMyAgent)
    print(f"\n{BOLD}[2/2] Menyinkronkan Repositori OverhaulMyAgent ke GitHub (Zero-PII)...{RESET}")
    github_success = False
    if os.path.exists(SYNC_GITHUB_PY):
        print(f"  -> Menjalankan {os.path.basename(SYNC_GITHUB_PY)}...")
        res_gh = subprocess.run([sys.executable, SYNC_GITHUB_PY], capture_output=False)
        if res_gh.returncode == 0:
            github_success = True
            print(f"  {GREEN}[✓] GitHub OverhaulMyAgent berhasil diperbarui & diverifikasi.{RESET}")
        else:
            print(f"  {YELLOW}[!] sync_overhaul_github.py keluar dengan kode {res_gh.returncode}{RESET}")
    else:
        print(f"  {YELLOW}[!] Script {SYNC_GITHUB_PY} tidak ditemukan.{RESET}")

    # Summary
    print(f"\n{BOLD}{CYAN}=================================================================={RESET}")
    print(f"{BOLD}{CYAN}  HASIL SINKRONISASI DUA JALUR (DUAL-PIPELINE)                     {RESET}")
    print(f"{BOLD}{CYAN}=================================================================={RESET}")
    print(f"  - Pipeline Google Drive (Private Full) : {'[✓] BERHASIL' if gdrive_success else '[!] CEK LOG'}")
    print(f"  - Pipeline GitHub (OverhaulMyAgent)    : {'[✓] BERHASIL' if github_success else '[!] CEK LOG'}")
    print(f"{BOLD}{CYAN}=================================================================={RESET}\n")


if __name__ == "__main__":
    main()
