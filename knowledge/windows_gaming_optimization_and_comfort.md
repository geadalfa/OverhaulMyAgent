# Windows Heavy Gaming Optimization, Thermal Efficiency & Anti-Motion-Sickness Protocol

Comprehensive engineering guide, technical knowledge base, and heuristic rules for AI Agent (Gemi) to optimize demanding Windows PC games (such as *Red Dead Redemption 2*, *Warhammer 40,000: Space Marine 2*, *Total War: Warhammer 3*, *The Witcher 3 Next-Gen*, etc.).

Primary Objectives:
1. **Pareto Efficiency ("The Sweet Spot")**: Eliminate compute overhead imperceptible to human eyes while preserving sharp, uncompromised visuals.
2. **Thermal & Hardware Protection**: Eliminate wasted GPU/CPU cycles, reduce wattage, and lower thermal output to keep the room cool.
3. **User's Anti-Motion-Sickness Ergonomics**: Prevent vestibular-visual sensory conflicts (nausea, dizziness, eye fatigue) on motion-sensitive displays.

---

## 1. User's Ergonomic Profile (Mandatory Anti-Motion-Sickness Invariants)

User experiences heightened sensitivity to visual-vestibular motion sickness during fast camera rotations or FPS gameplay. High temperatures in the room also exacerbate fatigue. The goal is a cool-running PC with crisp, artifact-free visuals.

### Zero-Nausea Ergonomic Checklist (Mandatory Active)
Whenever Gemi analyzes, recommends, or generates game configurations for User:

1. **Optimal Field of View (FOV: 90° – 105°)**:
   - *Root Cause:* Default console FOVs (60°–75°) create fishbowl tunnel vision on desktop monitors, confusing vestibular motion perception.
   - *Solution:* Increase FOV to at least **90°** (up to **100°–105°** on 16:9 or ultrawide displays) to align peripheral optic flow with monitor viewing distance.
2. **Motion Blur STRICTLY OFF (0% / Disabled)**:
   - *Root Cause:* Rotational camera blur and per-object blur destroy visual clarity and trigger inner-ear sensory conflict.
   - *Solution:* Completely disable all Camera Motion Blur and Object Motion Blur.
3. **Camera Shake & Head Bobbing ZERO / OFF**:
   - *Root Cause:* Head bobbing while sprinting and camera shake during explosions force continuous ocular refocusing.
   - *Solution:* Set Camera Shake, Head Bobbing, Weapon Sway, and Camera Recoil to **0% / Off**.
4. **Frame Pacing & Stutter Elimination (1% Low FPS Focus)**:
   - *Root Cause:* Micro-stuttering and wild frametime variance (e.g. 40 FPS -> 90 FPS -> 35 FPS) cause visual disorientation.
   - *Solution:* Lock the frame rate (*Frame Rate Cap*) at a consistent number (e.g., 60, 75, or 90 FPS) using NVIDIA driver limiter or RTSS. Consistent frametimes are vastly superior to erratic high framerates.
5. **Disable Optical Distortions (Chromatic Aberration, Vignette, Film Grain)**:
   - *Root Cause:* Rainbow prism fringing and darkened corners strain peripheral vision.
   - *Solution:* Disable Chromatic Aberration, Vignette, and Film Grain.
6. **Depth of Field (DoF) Disabled or Minimal**:
   - *Root Cause:* Artificial background blur forces eye muscles to fight the engine's synthetic focal depth.
   - *Solution:* Disable Depth of Field for gameplay.
7. **Static Center Reticle / Anchor Dot Enabled**:
   - *Root Cause:* The brain requires a fixed visual anchor point in the screen center to counteract rotational motion disorientation.
   - *Solution:* Enable persistent center crosshairs or accessibility center dots where available.

---

## 2. Graphics Hierarchy: Visual Impact vs. Performance Cost

True optimization is not setting everything to "Low". Low settings degrade visual fidelity without necessarily reducing heat if the framerate remains uncapped. The objective is cutting heavy settings that yield near-zero perceptual benefit.

```
                    [ GRAPHICS SETTINGS HIERARCHY ]
┌─────────────────────────────────────────────────────────────┐
│ 🌟 MANDATORY HIGH / ULTRA (Light FPS Cost, Max Visuals)     │
│  - Texture Quality (High/Ultra - while VRAM < 90%)          │
│  - Anisotropic Filtering (16x - 0% FPS Cost, Sharp Ground)  │
│  - Mesh / Geometry Quality (High - Prevents Pop-in)         │
│  - Ambient Occlusion (Medium/High/SSAO - Object Depth)      │
├─────────────────────────────────────────────────────────────┤
│ ⚡ SWEET SPOT: MEDIUM / HIGH (Heavy Compute, Equal Visuals) │
│  - Volumetric Fog / Clouds / Lighting (Cut 15-25% GPU Load) │
│  - Shadow Quality & Contact Shadows (Ultra = Screenshots)   │
│  - Screen Space Reflections (SSR) & Water Physics (Medium)  │
│  - Crowd / Pedestrian Density (Relieves CPU Bottlenecks)    │
├─────────────────────────────────────────────────────────────┤
│ 🚀 HIGH-PRIORITY UPSCALING (Crisp Image + Cool Temperatures)│
│  - DLSS / XeSS / FSR in QUALITY Mode                        │
│  - Updated DLSS DLLs (Prevents Ghosting / Smearing)         │
│  - RCAS / DLSS Sharpening (0.15 - 0.3) & Mip-Map Bias       │
└─────────────────────────────────────────────────────────────┘
```

### A. High Visual Preservation Settings
1. **Texture Quality**: Keep at **High** or **Ultra** as long as VRAM utilization remains under **90%**. Modern GPUs handle high-resolution textures with negligible performance penalty if VRAM is sufficient.
2. **Anisotropic Filtering (16x)**: Force to **16x**. Sub-0.5% GPU cost, ensuring oblique angle ground and wall textures remain sharp.
3. **Ambient Occlusion (Medium / SSAO)**: Never disable completely. Disabling AO strips scene depth, making objects appear flat and floating.

### B. "Ultra is for Screenshots" (Cut to Medium/High)
1. **Volumetric Fog / Clouds / Lighting**: Ultra uses dense raymarched steps. Reducing to **Medium** or **High** immediately cuts GPU load by **15%–25%** with virtually indistinguishable visual difference in motion.
2. **Shadow Quality**: Dropping from Ultra to **High** or **Medium** produces natural shadow penumbras without shimmering.
3. **Water Physics & SSR**: Ultra water simulation consumes extreme compute. Setting to **25%–50%** or **Medium** maintains realistic reflections.
4. **Ray Tracing**: Disable Ray Tracing (especially RT Reflections) if room heat becomes an issue, unless utilizing DLSS Frame Generation on RTX 40 series GPUs.

---

## 3. Thermal & Power Control Strategies

Room heat during gaming stems from **uncapped GPU and CPU power dissipation**, exhausting hundreds of Watts into the room.

### A. Frame Rate Limiting (The Primary Heat Cut)
- **Problem:** If a monitor displays 60Hz or 75Hz, but the GPU renders 120 FPS, 45–60 frames per second are wasted computation, exhausting excess heat and inducing tearing.
- **Solution:**
  - Cap framerates via **NVIDIA Control Panel / Profile Inspector (Frame Rate Limiter V3)** or **RivaTuner Statistics Server (RTSS)**.
  - 60Hz Display: Lock at **60 FPS** (or **58 FPS** with G-Sync/VRR + V-Sync + Reflex).
  - 75Hz / 120Hz / 144Hz Display: Lock at the highest consistently sustainable framerate (e.g., **72 FPS**, **90 FPS**, or **120 FPS**).
  - **Thermal Impact:** Dropping GPU load from 99% to 70–80% cuts power draw by **40–80 Watts**, reducing GPU temps by **8°C–15°C** and lowering fan noise.

### B. Undervolting & Power Limiting
- Setting a GPU **Power Limit** of **85%–90%** via MSI Afterburner or NVAPI retains ~98% of peak performance while cutting power and heat dramatically.
- V/F curve undervolting allows the GPU to sustain high boost clocks at lower voltages (e.g., 900mV instead of 1050mV).

### C. CPU Affinity & P-Core Management
- On modern hybrid architectures (Intel 12th–15th Gen with P/E-cores), prioritize binding game processes to **Performance Cores (P-Cores)** to eliminate scheduling stutters.

---

## 4. Heavy Game Engine Profiles & Sweet Spots

### 1. Red Dead Redemption 2 (RAGE Engine)
- **Bottlenecks:** GPU heavy on Volumetrics and Water Physics.
- **Optimal API:** **Vulkan** (smoother frametimes and higher 1% lows than DirectX 12).
- **Config Path:** `%USERPROFILE%\Documents\Rockstar Games\Red Dead Redemption 2\Settings\system.xml`.
- **Sweet Spot Settings:**
  - `textureQuality`: **Ultra**
  - `volumetricsQuality`: **Medium**
  - `waterQuality`: **Medium** / Water Physics Slider at **25% - 50%**
  - `shadowQuality`: **High**
  - `asyncComputeEnabled`: `"true"`
  - `DLSS`: **Quality** mode with updated DLL
  - `FOV`: Max in-game slider.
  - `Camera Shake`: Minimal / Off.

### 2. Warhammer 40,000: Space Marine 2 (Swarm Engine)
- **Bottlenecks:** Heavily **CPU bound** due to swarm AI and physics simulation for thousands of Tyranids.
- **Optimization Strategy:**
  - Lowering resolution will not increase FPS if CPU load is 95–100%.
  - Reduce CPU-heavy settings: *Object Detail* to **High/Medium**, *Cloth Simulation* to **Medium**.
  - Use **DLSS Quality** for armor crispness.
  - Lock FPS to 60 to prevent CPU thermal saturation.
  - Disable Motion Blur & set FOV to 90°+.

### 3. Total War: Warhammer 3 (Warscape Engine)
- **Bottlenecks:** Heavy **CPU & VRAM** bottlenecks during massive unit clashes and campaign map rendering.
- **Config Path:** `%APPDATA%\The Creative Assembly\Warhammer3\scripts\preferences.script.txt`.
- **Sweet Spot Settings:**
  - `Unit Size`: **Ultra** (strong CPU) or **High** (CPU bound).
  - `Porthole Quality`: Change from **3D** to **2D** (huge performance saver; 3D unit portraits waste rendering cycles).
  - `Shadows`: **Medium**.
  - `VFX Detail`: **Medium** (prevents frame drops during spell effects).
  - `Corpse Lifespan`: Lower duration to reduce late-battle CPU/VRAM load.

### 4. The Witcher 3: Wild Hunt Next-Gen (REDengine 4 / DX12)
- **Bottlenecks:** GPU heavy on Ray Tracing; CPU heavy on Novigrad NPC crowd density.
- **Config Path:** `%USERPROFILE%\Documents\The Witcher 3\dx12user.settings`.
- **Sweet Spot Settings:**
  - `HairWorks`: **Off** (costs 15–25 FPS for minor hair strands).
  - `Ray Tracing`: Disable completely if room heat is an issue, or use RT Global Illumination paired with DLSS Quality + Frame Generation on RTX 40 series.
  - `Number of Background Characters`: **High** (relieves Novigrad CPU load).
  - `Texture Quality`: **Ultra+**.
  - `Motion Blur & Blur`: **Off**.

---

## 5. Tooling, APIs & Open-Source Manifests

| Tool / Repository | Source URL | Purpose & Integration |
| :--- | :--- | :--- |
| **Ludusavi Manifest** | `github.com/mtkennerly/ludusavi-manifest` | Massive YAML database mapping config paths (`.ini`, `.xml`, `.txt`, registry) for thousands of games. |
| **PCGamingWiki Cargo API** | `pcgamingwiki.com/wiki/PCGamingWiki:API` | MediaWiki Cargo queries for FPS limits, FOV support, config file paths, and stutter fixes. |
| **r/OptimizedGaming** | `reddit.com/r/OptimizedGaming/.json` | Verified graphics presets from Digital Foundry and Hardware Unboxed. |
| **Intel PresentMon** | `github.com/GameTechDev/PresentMon` | CLI headless telemetry (`msBetweenPresents`, `msGPUActive`, `msCPUWait`) identifying CPU vs GPU bottlenecks. |
| **CapFrameX** | `github.com/CXWorld/CapFrameX` | Mathematical formulas for 1% Low FPS, 0.1% Low FPS, and frametime variance. |
| **LibreHardwareMonitor** | `github.com/LibreHardwareMonitor` | Hardware telemetry reading CPU Package temps, GPU Core/Hotspot, wattage, and VRAM utilization. |
| **DLSS Swapper** | `github.com/beeradmoore/dlss-swapper` | Upgrades `nvngx_dlss.dll` to recent stable versions to eliminate ghosting and smearing. |
| **OptiScaler** | `github.com/optiscaler/OptiScaler` | Open-source upscaler middleware injecting RCAS sharpening, mip-map bias adjustments, and Frame Generation. |
| **NVIDIA Profile Inspector** | `github.com/Orbmu2k/nvidiaProfileInspector` | CLI execution (`-silentImport Profile.nip`) for Resizable BAR, Frame Rate Limiter V3, and driver-level DLSS tuning. |
| **Chris Titus Tech WinUtil** | `github.com/ChrisTitusTech/winutil` | Windows JSON tweaks (`tweaks.json`) disabling background indexing, telemetry, and enabling ultimate performance power profiles. |

---

## 6. The 7 Golden Guardrails for Gemi

1. **Rule 1: Visual Preservation ("Anti-Slop Visuals")**: Never drop *Texture Quality* below *High* unless VRAM usage exceeds 90%. Never disable *Ambient Occlusion* completely.
2. **Rule 2: Anti-Motion-Sickness Mandate**: Always enforce Motion Blur **OFF**, Camera Shake **OFF/0%**, FOV at **90°–105°**, and eliminate optical distortion (Chromatic Aberration/Vignette).
3. **Rule 3: Upscaling Priority**: Before degrading geometry or lighting to Low, prioritize **DLSS / XeSS / FSR in Quality Mode**.
4. **Rule 4: "Ultra is for Screenshots"**: Reduce Volumetrics, Shadows, Clouds, and SSR from Ultra to High/Medium to cut 20–30% overhead with zero visual penalty in motion.
5. **Rule 5: Frame Pacing & Thermal Cap**: Cap framerate slightly below the monitor refresh rate to stabilize 1% lows and dramatically lower GPU temperatures.
6. **Rule 6: Automated Backup**: Always create a `.bak` backup before modifying any game configuration file (`.ini`, `.xml`, `.txt`).
7. **Rule 7: Anti-Cheat Compliance**: Never modify DLLs or inject memory into games protected by active Anti-Cheat systems (Easy Anti-Cheat, BattlEye, Vanguard).
