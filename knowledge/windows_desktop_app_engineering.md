# Windows Desktop Application Engineering Guide (Zero-Crash & Clean Antivirus Compliance)

Deterministic engineering standards for designing, building, packaging, and distributing standalone Windows desktop applications (using Python, Webview/Edge App Mode, PyInstaller, and Inno Setup) ensuring high runtime stability, zero crashes, and clean antivirus reputation without false-positive triggers.

---

## 1. Zero-Crash Architecture (Preventing Runtime Halts & Unhandled Crashes)

### 1.1. Mandatory `sys.stdout` & `sys.stderr` Protection in Windowed Mode
* **Root Cause:** When compiled with `--windowed` / `--noconsole` in PyInstaller, Windows disables standard console streams. In this state, `sys.stdout` and `sys.stderr` evaluate to `None`. Any invocation of `print()` or library logging attempting to write to stdout throws a fatal unhandled error:
  ```text
  AttributeError: 'NoneType' object has no attribute 'write'
  ```
* **Mandatory Solution:** Redirect streams at the very top of application entry points (`server.py` / `main.py`):
  ```python
  import os
  import sys

  if sys.stdout is None:
      try:
          sys.stdout = open(os.devnull, "w")
      except Exception:
          pass
  if sys.stderr is None:
      try:
          sys.stderr = open(os.devnull, "w")
      except Exception:
          pass
  ```

### 1.2. 100% Silent Windows Subprocess Execution (No Flashing CMD Window)
* **Root Cause:** Invoking `subprocess.run(["powershell", ...])` or `cmd.exe` from a GUI application flashes a black console window unless window flags are explicitly specified.
* **Mandatory Solution:** Combine `CREATE_NO_WINDOW` (`0x08000000`) and `STARTF_USESHOWWINDOW (SW_HIDE)`:
  ```python
  startupinfo = None
  creationflags = 0
  if os.name == "nt":
      startupinfo = subprocess.STARTUPINFO()
      startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
      startupinfo.wShowWindow = 0  # SW_HIDE
      creationflags = 0x08000000   # CREATE_NO_WINDOW

  p = subprocess.run(
      ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", script],
      capture_output=True,
      text=True,
      timeout=15,
      startupinfo=startupinfo,
      creationflags=creationflags,
  )
  ```

### 1.3. Single-Pass Telemetry Queries & Layered Fallbacks
* Avoid calling multiple sequential subprocesses in tight loops. Aggregate telemetry queries into a single batch PowerShell/WMI script returning a consolidated JSON structure in ~1 second.
* Provide robust fallback paths (e.g., if `Get-PhysicalDisk` fails due to restricted privileges or legacy storage drivers, automatically fall back to `Win32_DiskDrive`).

### 1.4. Threaded Server & Background Cache Pre-Warming
* Implement `ThreadingHTTPServer` so static asset requests (HTML/CSS/JS/Icons) are never blocked by hardware I/O scans.
* Pre-warm telemetry cache in a background thread upon server startup (`prewarm_cache()`). When the frontend webview initializes, disk telemetry is immediately available in memory, rendering without socket timeouts.

### 1.5. Port Conflict Management & Single-Instance Locking
* Verify whether the local port (`127.0.0.1:5550`) is already bound before attempting socket binding.
* If active, trigger the existing window focus handler and exit cleanly (`exit(0)`) from the secondary process.

---

## 2. Windows Taskbar Icon Customization (Edge/Chrome App Mode)

### Why Generic Browser / Globe Icons Appear on the Taskbar
When local web apps launch via `msedge.exe --app=http://...`, Windows groups the window under the primary Edge process and defaults to a web globe icon if PWA metadata is incomplete.

### Resolution Steps:
1. **Isolated User Data Directory (`--user-data-dir`):**
   ```python
   user_data_dir = os.path.join(os.environ.get("LOCALAPPDATA", "."), "AppName_Profile")
   subprocess.Popen([
       "msedge.exe",
       f"--app={url}",
       f"--user-data-dir={user_data_dir}",
       "--window-size=1200,850",
       "--disable-extensions"
   ])
   ```
2. **Web App Manifest (`manifest.json`):**
   Define `display: standalone`, `name`, and an `icons` array containing 192x192 and 512x512 PNG entries.
3. **Multi-Resolution Icon File:**
   Embed a `.ico` file containing complete mipmap layers (16x16, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256).

---

## 3. Antivirus False-Positive Prevention Protocol (Clean Compliance)

### 3.1. Why PyInstaller Applications Trigger Heuristic Alerts
1. **UPX Compression Packer:** The `--upx` flag compresses binary sections, a technique frequently used by malware droppers to obfuscate signatures. Heuristic scanners (Windows Defender, CrowdStrike, Kaspersky) flag UPX-packed binaries as `Trojan.Generic` or `Heur.Suspicious`.
2. **`%TEMP%` Extraction in `--onefile`:** The `--onefile` mode unpacks dozens of `.dll`, `.pyd`, and executable files into `C:\Users\<User>\AppData\Local\Temp\_MEIxxxxxx` on every launch, triggering behavioral heuristic alerts characteristic of dropper malware.
3. **Missing PE Header Metadata:** Executables without official CompanyName, FileDescription, Version, and Icon entries are categorized as high-risk anonymous binaries.

### 3.2. Clean Distribution Standard:
1. **Use `--onedir` Mode (Avoid `--onefile`):**  
   Compiling with `--onedir` retains DLLs in a static, transparent `_internal` directory, eliminating runtime unpacking.
2. **Never Use UPX Compression:**  
   Always specify `--noupx` or ensure UPX is disabled in PyInstaller build specs.
3. **Package with Inno Setup:**  
   - Inno Setup generates structured installer binaries recognized and trusted by Windows SmartScreen and antivirus heuristics.
   - Ultra-compression (`lzma2/ultra64`) yields compact bundle sizes (~6MB) without corrupting PE header integrity.
   - Target standard non-elevated user directories: `{localappdata}\Programs\{AppName}` (eliminating suspicious UAC elevation prompts).
   - Embed official icon files (`SetupIconFile`) and clean uninstaller registration (`UninstallDisplayIcon`).
4. **Transparency & Code Signing:**
   - For open-source releases, publish source code openly on GitHub with tagged releases and SHA-256 checksums.
   - When available, sign installers and executable binaries with `signtool.exe` using a valid Code Signing Certificate.

---

## 4. Pre-Release Verification Checklist:
- [x] `sys.stdout` & `sys.stderr` safety fallbacks implemented for `--windowed` mode.
- [x] All Windows subprocesses configured with `CREATE_NO_WINDOW` & `SW_HIDE`.
- [x] Single-pass telemetry querying with layered fallbacks.
- [x] Threaded server with background cache pre-warming for zero-lag rendering.
- [x] Single-instance detection on local TCP ports.
- [x] `--onedir` compilation without UPX in PyInstaller.
- [x] Multi-resolution `.ico` embedded into the executable PE header.
- [x] Packaged via Inno Setup with standard user privileges (`PrivilegesRequired=lowest`).
- [x] Clean uninstaller integrated with Windows Settings & Control Panel.
