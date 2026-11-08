# REA (Reverse Engineer Anything) Architecture, Protocol & Agent Integration

## 1. System Identity & Overview
- **Project:** REA (`morluto/rea`, Version 6.4.0) — [rea.tools](https://rea.tools/).
- **Repository:** `https://github.com/morluto/rea`
- **Core Directive:** Local-first, evidence-backed reverse engineering toolkit and Model Context Protocol (MCP) server. Bridges AI coding agents (Antigravity, Claude Code, Cursor, Gemini CLI) to disassemble, decompile, trace, and reconstruct software without original source code.
- **Local Environment & Registry:**
  - Package: Globally installed via npm `rea-agents@6.4.0`.
  - Executable: `~\AppData\Roaming\npm\rea.cmd` (Node.js runtime: `C:\Program Files\nodejs\node.exe`).
  - MCP Entry Point: `~\AppData\Roaming\npm\node_modules\rea-agents\scripts\rea.mjs mcp`.
  - MCP Registration: Registered as `rea` in `~/.gemini/config/mcp_config.json`.
  - Skill Directory: `~/.gemini/config/skills/reverse-engineer-anything\SKILL.md` (with deep guides in `references/`).
  - Diagnostics: Validated via `rea mcp doctor` (170 MCP tools, 6 prompt workflows, MCP protocol version 2025-11-25).
  - Windows Execution Invariant: PowerShell execution policies block `rea.ps1`. When executing CLI commands in scripts/terminals, invoke via `cmd /c rea <args>` or `node <script_path> <args>`.

---

## 2. Core Epistemic Principles & Reversing Invariants
REA enforces strict deterministic engineering rules designed to prevent hallucination in reverse engineering:

1. **Evidence-Backed Reconstructions (Zero Vibe Reversing):**
   - Every factual claim about binary structure, API calls, logic flow, or data models must cite a stable `evidence_id` returned by REA tools.
   - Decompiler pseudocode and addresses are analysis observations, NOT canonical original source code.
   - Reconstructed code must be verified against original binary bytes or execution traces.

2. **Strict Epistemic Classification:**
   - **Observed:** Direct factual evidence present in the binary/artifact (e.g. raw opcodes, string literals, export symbols, manifest entries, packet bytes).
   - **Inferred:** Decompiler deductions, variable types, decompiled control flow, or heuristic reconstructions.
   - **Unknown:** Facts not proved by the binary or available tools (e.g. missing symbols, dynamic runtime behavior, stripped type info). Track via `record_unknown` and `update_unknown`.

3. **Summary-First & Bounded Token Hygiene:**
   - For large binaries, JavaScript packages, or ELF layouts, always start with `"detail": "summary"`.
   - Never flood LLM context with multi-megabyte disassemblies. Use `inspect_analysis_view` to read targeted facets (e.g. `value_flow_operations`, `referenced_strings`, `callers`, `callees`) using the parent `evidence_id`.
   - When MCP returns `resource_constraint` (`details.resource: "transport"`), page using `inspect_analysis_view` or export the full session via `export_evidence_bundle`.

4. **Lifecycle & Active Session Cleanliness:**
   - Target-free tools (`analyze_javascript_application`, `inspect_binary_layout`, `inspect_pe_resources`, `inspect_evm_interface`) run directly on supplied paths.
   - Active-target native tools require opening a session with `open_binary`.
   - Always close opened native sessions with `close_binary` upon investigation completion to free engine memory and file locks.

---

## 3. The 7 Target Disciplines & Modality Matrix

### 3.1. Native Executables & Libraries (PE, ELF, Mach-O, DOS MZ)
- **Engines & Providers:** Ghidra (`GHIDRA_INSTALL_DIR`), IDA Pro (`REA_IDA_MCP_CONFIG` via `ida-pro-mcp`), Hopper (`hopper-v4`), and LLDB.
- **Key Operations:**
  - `open_binary`: Binds native target binary; supports provider selection (`ghidra`, `ida`, `hopper`).
  - `binary_overview`: Architecture, endianness, bitness, entry point, compiler signatures.
  - `analyze_function`: Comprehensive function dossier (assembly, pseudocode, basic blocks, callers, callees, def-use value flow).
  - `search_strings`, `search_procedures`: Fast cross-binary indexing.
  - `xrefs`: Bounded incoming and outgoing references to addresses/symbols.
  - `read_bytes`, `address_to_file_offset`: Byte-level inspection and mapping to disk offsets.
  - `observe_native_calls`: LLDB-driven dynamic execution observation with bounded breakpoints (`duration_ms`, `max_events`).
  - `close_binary`: Session cleanup.

### 3.2. Managed .NET Assemblies (CIL, PE/CLI, NativeAOT)
- **Static Inspection (Zero Execution):**
  - `inspect_managed_artifact`: Reads PE/CLI headers, metadata streams, runtime versions, assembly refs.
  - `inspect_managed_members`: Type declarations, method signatures, CIL instructions, member tokens.
  - `inspect_managed_native_boundaries`: P/Invoke declarations, DllImport signatures, unmanaged interop.
  - `verify_managed_native_boundaries`: Cross-references P/Invoke declarations against native export evidence.
- **.NET NativeAOT Routing:** NativeAOT compiles CIL into machine code. If metadata/CIL is absent, REA routes to the native Ghidra/IDA workflow rather than failing managed decompilation.

### 3.3. JavaScript & Electron Applications (ASAR, Bundles, Source Maps)
- **Static Structural Graph:**
  - `analyze_javascript_application`: Inspects ASAR archives or extracted trees, resolving modules, imports, routes, and IPC channels.
  - `recover_javascript_sources`: Extracts verified readable JS modules with provenance tracking.
  - `trace_javascript_semantics`: Traces variable flows, exports, and module relations.
  - `trace_application_feature`: Propagates a seed token/feature across the semantic graph.
  - `compare_javascript_export_shapes`: Type and shape comparison across versions without execution.
- **Runtime Reconciliation:**
  - `list_electron_targets`, `capture_electron_scenario`: Connects to running Electron instances.
  - `reconcile_javascript_runtime`: Correlates static AST/bundle graphs with observed runtime executions.

### 3.4. Android Application Ecosystem (APK, AAB, DEX, ADB)
- **Static APK Analysis:**
  - `inspect_android_package`: Manifest declarations, activities, services, permissions, exported components.
  - `search_android_classes`, `inspect_android_class`: DEX class hierarchy, member definitions.
  - `inspect_android_method`: Bytecode/smali decompilation for targeted methods.
  - `trace_android_references`: Call hierarchy and incoming class references.
  - `decode_android_resources`: Apktool integration for XML layouts, string tables, asset manifests.
- **Hardware / Emulator ADB Bridge:**
  - `list_adb_devices`, `inspect_adb_device`, `inspect_adb_package`: Device telemetry and dumpsys.
  - `pull_adb_package`, `pull_adb_file`, `push_adb_file`: File transfer with SHA-256 verification.
  - `read_adb_logcat`: Bounded device log buffer capture.
  - `start_adb_app`, `stop_adb_app`, `start_adb_activity`: Controlled intent and lifecycle triggering.
  - `capture_adb_screen`: Digest-verified UI screen capture.

### 3.5. Apple Platform Artifacts (macOS, iOS, IPA, Mach-O)
- **Anatomy & Metadata:**
  - `inspect_macho`, `inspect_plist`, `list_architectures`: Mach-O fat headers, code signing, entitlements.
  - `demangle_swift`: Offline Swift symbol demangling.
  - `trace_dylib_resolution`: Dyld `@rpath`, `@executable_path`, and shared cache load tracing.
  - `decode_interface_builder`: Nib and Storyboard asset decoding.
  - `project_apple_application_graph`: End-to-end component graph projection.

### 3.6. Web & Network Runtime Analysis (CDP, WebMCP, Mitmproxy)
- **Passive Browser Observation:**
  - `list_browser_targets`, `inspect_web_page`: Chrome DevTools Protocol (CDP) session connection.
  - `observe_web_execution`: Execution counter, call-frequency, and optimization observation.
  - `discover_webmcp_tools`: Discovers web-exposed agent tools and API endpoints.
  - `capture_web_screenshot`, `compare_web_screenshots`: Visual regression verification.
  - `capture_browser_scenario`: Playwright-driven scenario execution with structured Evidence return.
- **Network Captures:**
  - `inspect_web_network_capture`: Offline HAR and native mitmproxy capture inspection.
  - `export_web_scripts`: Exports retained scripts for offline static code auditing.
  - `trace_web_module_imports`, `trace_web_source_location`: Source-map anchoring.

### 3.7. Firmware, Bytecode & Crash Artifacts
- **Firmware:** `inspect_firmware_regions` and `extract_firmware` via Binwalk / Unblob.
- **EVM Bytecode:** `inspect_evm_interface` extracts dispatch selectors, calldata offsets, and mutability.
- **Recorded Linux Crashes:** `inspect_recorded_crash` inspects x86-64 ELF cores, register states, notes, and memory mappings via pwntools and GDB/pwndbg.
- **Process Capture:** `capture_process_scenario` observes terminal execution, exit codes, and file mutations under native PTY.

---

## 4. Evidence Workflows & Reconstruction Obligation Ledger

### 4.1. Evidence Architecture
- Every operation yields an envelope containing:
  - `evidence_id`: SHA-256 anchored unique reference.
  - `normalized_result`: Structured, typed data payload.
  - `authority`: Identifying tool/engine (e.g. `ghidra`, `jadx`, `rea_managed`).
  - `limitations`: Declared boundaries (e.g. missing debug symbols, stripped types).
- When responses exceed context or transport thresholds, REA stores the complete record in session storage, returning `parent_evidence_id`. Agents inspect views using:
  ```json
  inspect_analysis_view({
    "parent_evidence_id": "evi_...",
    "view": { "kind": "native", "facet": "value_flow_operations", "offset": 0, "limit": 32 }
  })
  ```

### 4.2. Reconstruction Obligation Ledger
- `build_reconstruction_obligation_ledger`: Compiles all declared functions, routes, or members into an obligation checklist.
- `evaluate_reconstruction_coverage`: Evaluates reconstructed implementations against evidence, enforcing a fail-closed boundary.
- `verify_reconstruction`: Verifies behavioral equivalence against unit test cases or byte assertions (as demonstrated in the DX-Ball and TH04 showcases).

---

## 5. Case Study: Windows Update & Pre-Shutdown Servicing Internals
Empirical evidence uncovered through REA analysis of Windows system binaries (`StartMenuExperienceHost.exe`, `TrustedInstaller.exe`, `UsoSvc.dll`, `cbscore.dll`):

### 5.1. The Pre-Shutdown Servicing Trap
1. **Shutdown Mechanism:**
   - User triggers Start Menu shutdown -> Explorer calls `InitiateShutdownW`.
   - Service Control Manager (SCM) issues `SERVICE_CONTROL_PRESHUTDOWN` to registered listeners.
2. **CBS Servicing Hook:**
   - `TrustedInstaller` and Update Session Orchestrator (`UsoSvc`) subscribe with `SERVICE_ACCEPT_PRESHUTDOWN`.
   - If packages have staged into `Installed-PendingReboot` within the Component Based Servicing (CBS) store, CBS commits transactions immediately during the shutdown sequence before ACPI power cut.
   - The registry tweak `ShutdownFlyoutOptions = 0` only hides the UI badge in `StartMenuExperienceHost.exe`; it does NOT unregister CBS from SCM pre-shutdown events.

### 5.2. Verified Solution Matrix
1. **Group Policy AUOptions = 2 (Root Prevention):**
   - Registry `HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU` -> `AUOptions = 2`.
   - Windows never automatically downloads or stages packages into `Installed-PendingReboot`.
2. **Direct Kernel Shutdown (`shutdown /s /f /t 0`):**
   - Bypasses Explorer and the standard SCM pre-shutdown orchestration, directly signaling the Windows NT kernel to terminate user processes and cut ACPI power immediately.
