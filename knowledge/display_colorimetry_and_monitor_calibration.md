# Display Colorimetry & Computer Monitor Calibration Engineering

Comprehensive architectural guide, colorimetric science foundation, hardware control protocols (VESA MCCS / DDC/CI), OS/GPU color management pipelines, and deterministic calibration steering for AI agents.

---

## 1. Mathematical Foundations of Color Science

### 1.1. Color Spaces & Chromaticity Coordinates
All colors discernible by the human visual system are mapped within the CIE 1931 $(x, y)$ chromaticity diagram or the perceptually uniform CIE 1976 $(u', v')$ chromaticity space. Standard display color gamuts are defined by their RGB primary chromaticity coordinates:

| Color Gamut | Red $(x, y)$ | Green $(x, y)$ | Blue $(x, y)$ | White Point $(x, y)$ | Primary Application |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **sRGB / Rec. 709** | $(0.6400, 0.3300)$ | $(0.3000, 0.6000)$ | $(0.1500, 0.0600)$ | D65 $(0.3127, 0.3290)$ | Standard Windows OS, Web, SDR video, productivity |
| **DCI-P3 (Theater)**| $(0.6800, 0.3200)$ | $(0.2650, 0.6900)$ | $(0.1500, 0.0600)$ | Theater $(0.3140, 0.3510)$| Digital cinema projection |
| **Display P3** | $(0.6800, 0.3200)$ | $(0.2650, 0.6900)$ | $(0.1500, 0.0600)$ | D65 $(0.3127, 0.3290)$ | Apple displays, wide-gamut monitors, HDR |
| **Adobe RGB (1998)**| $(0.6400, 0.3300)$ | $(0.2100, 0.7100)$ | $(0.1500, 0.0600)$ | D65 $(0.3127, 0.3290)$ | CMYK prepress printing, photography |
| **Rec. 2020 (BT.2020)**| $(0.7080, 0.2920)$ | $(0.1700, 0.7970)$ | $(0.1310, 0.0460)$ | D65 $(0.3127, 0.3290)$ | Ultra HD HDR container specification |

### 1.2. White Point & Correlated Color Temperature (CCT)
- **CIE Standard Illuminant D65:** Standard daylight reference at $6504\text{ K}$, exactly at chromaticity coordinates $x = 0.3127, y = 0.3290$.
- **Planckian Locus & Duv:** Any deviation perpendicular to the blackbody locus creates color tint:
  - $\Delta uv > 0$ (above locus): Greenish tint.
  - $\Delta uv < 0$ (below locus): Magenta / reddish tint.
  - Target tolerance for professional calibration: $|\Delta uv| \le 0.001$.

### 1.3. Electro-Optical Transfer Function (EOTF / Gamma)
EOTF governs the non-linear relationship between input digital code values ($V \in [0, 1]$) and physical display luminance ($L \in [0, L_{\text{max}}]$):
- **Pure Power Gamma 2.2:** $L = L_{\text{max}} \cdot V^{2.2}$ (Standard desktop environment with ambient illumination).
- **sRGB Piecewise Curve:** Linear segment for near-black ($V \le 0.04045 \implies L = L_{\text{max}} \cdot \frac{V}{12.92}$) followed by power $2.4$ with offset.
- **BT.1886:** EOTF for mastering SDR broadcast content in dark environments ($L = a \cdot \max(V + b, 0)^{2.4}$).
- **SMPTE ST 2084 (Perceptual Quantizer / PQ):** Absolute luminance transfer curve for HDR up to $10{,}000\text{ nits}$.

### 1.4. Color Difference Metric: CIEDE2000 ($\Delta E_{00}$)
Calculated in the uniform $L^*a^*b^*$ color space incorporating lightness, chroma, and hue differences with rotation factor $R_T$ for blue region non-linearities:
$$\Delta E_{00} = \sqrt{\left(\frac{\Delta L'}{k_L S_L}\right)^2 + \left(\frac{\Delta C'}{k_C S_C}\right)^2 + \left(\frac{\Delta H'}{k_H S_H}\right)^2 + R_T \left(\frac{\Delta C'}{k_C S_C}\right)\left(\frac{\Delta H'}{k_H S_H}\right)}$$

**Evaluation Benchmarks:**
- $\Delta E_{00} < 1.0$: Imperceptible to the trained human eye (Studio Reference Grade).
- $1.0 \le \Delta E_{00} \le 2.0$: Perceptible only through direct side-by-side comparison (Design & Color Grading Standard).
- $2.0 < \Delta E_{00} \le 3.0$: Acceptable for general consumer viewing; noticeable upon scrutiny.
- $\Delta E_{00} > 3.0$: Readily visible color deviation requiring immediate recalibration.

### 1.5. Panel Physics Invariants
- **IPS / Fast IPS:** Superior off-axis chromatic stability ($\Delta E < 1.5$ up to $\pm 45^\circ$). Static contrast ratio limited to ~1000:1 to 1500:1. Susceptible to IPS glow in dark environments.
- **VA (Vertical Alignment):** High static contrast (3000:1 to 5000:1), deep blacks. Prone to off-axis gamma shift and dark-pixel transition smearing.
- **OLED / QD-OLED:** Infinite per-pixel contrast, true blacks ($0\text{ nits}$), instantaneous pixel response. Governed by Auto Brightness Limiter (ABL) in HDR; triangular or non-standard subpixel layouts require ClearType / text rendering optimization.

---

## 2. Hardware-First Calibration Hierarchy & System Invariants

### 2.1. Principle 1: Hardware-First Adjustment
```
1. Physical OSD / VCP Gain Adjustment (Red, Green, Blue Drive)
   └── Adjust hardware analog gains to hit D65 white point directly on panel
2. Monitor Contrast & Black Level Tuning (VCP 0x12, 0x6C-0x70)
   └── Ensure no white clipping (251-254) and no black crushing (1-16)
3. GPU Sinyal & Format Configuration
   └── RGB 4:4:4 Full Dynamic Range (0-255) + Hardware Dithering enabled
4. Gamut Management (OSD sRGB Clamp / Windows ACM / Driver Clamping)
   └── Clamp native wide gamut (125-150% sRGB) to standard sRGB targets
5. Software Profile / LUT (1D VCGT / 3D LUT)
   └── Only applied for final micro-corrections (ΔE residual cleanup)
```

> [!IMPORTANT]
> **Never raise RGB Gain above default:** When calibrating White Point to D65 ($x = 0.3127, y = 0.3290$) via hardware VCP codes (`0x16`, `0x18`, `0x1A`), **NEVER** increase any channel above its factory default (usually 100). Always attenuate the excess dominant channel(s) downward. Raising values above default causes ADC clipping, crushing near-white highlight steps.

### 2.2. Principle 2: Anti-Double-Clamping Invariant
Wide-gamut displays ($> 100\%$ sRGB) will severely over-saturate SDR colors unless clamped. However, multiple clamping layers will compound and wash out colors:
- If the monitor's OSD is set to an **sRGB Emulation Mode**, **DO NOT** enable GPU-level clamping (`novideo_srgb`, `dwm_lut`) or Windows 11 Auto Color Management (ACM) with an un-clamped wide gamut profile.
- If GPU-level clamping (`novideo_srgb` matrix or `dwm_lut`) is active, the wide-gamut ICC profile must **NOT** be assigned as default in Windows Color Management for color-managed applications.

### 2.3. Principle 3: SDR vs HDR Pipeline Isolation
- **SDR Pipeline:** Target sRGB / Rec.709 gamut, D65 white point, Gamma 2.2, target luminance $100\text{--}120\text{ cd/m}^2$ (dim room) or $140\text{--}180\text{ cd/m}^2$ (bright office).
- **HDR Pipeline:** Container Rec.2020 / DCI-P3 gamut, SMPTE ST 2084 PQ curve, peak luminance configured via Windows HDR Calibration tool to match display clipping boundary. No sRGB clamp permitted in HDR mode.

### 2.4. Principle 4: GPU Signal Integrity & Dithering
- **Format:** Always configure GPU output to `RGB 4:4:4 Full Range (0-255)`. Never use `YCbCr 4:2:2` or `Limited (16-235)`.
- **Dithering:** When injecting 1D LUTs (VCGT) or 3D LUTs into GPU hardware on an 8-bit panel, GPU Dithering (Spatial Blue-Noise or Temporal Dithering) **MUST** be enabled to eliminate banding artifacts across smooth gradients.

### 2.5. Principle 5: Motion Clarity & Overdrive Tuning
- Adjust monitor Overdrive (Response Time) proportionally to actual frame rates:
  - If refresh rate is high (240Hz) and FPS is capped lower (e.g. 75–120 FPS), using the fastest Overdrive preset ("Extreme" / "Boost") induces violent **Inverse Ghosting** (Overshoot / Corona).
  - Enforce standard/normal overdrive profiles under variable refresh rates (VRR / G-Sync / FreeSync) unless variable overdrive is natively hardware-tuned.

---

## 3. VESA MCCS & DDC/CI Hardware Protocol

### 3.1. Standard VCP Control Codes (VESA MCCS v2.2a)
Communication occurs over the I2C bus within DisplayPort, HDMI, or USB-C interfaces:

| VCP Code (Hex) | Control Name | Function & Operational Rule |
| :--- | :--- | :--- |
| `0x10` | **Luminance (Brightness)** | Backlight intensity ($0\text{--}100$). Sets target room nits without crushing dynamic range. |
| `0x12` | **Contrast** | Digital signal gain ($0\text{--}100$). Keep at factory default (typically 50 or 70) to prevent white clipping. |
| `0x14` | **Color Preset** | Select factory color presets (e.g., Warm 6500K, Cool 9300K, User Custom, sRGB). |
| `0x16` | **Video Gain (Red)** | Hardware red drive ($0\text{--}100$). Attenuate to remove reddish cast. |
| `0x18` | **Video Gain (Green)** | Hardware green drive ($0\text{--}100$). Attenuate to remove greenish cast. |
| `0x1A` | **Video Gain (Blue)** | Hardware blue drive ($0\text{--}100$). Attenuate to remove bluish cast. |
| `0x6C` | **Video Black Level (Red)** | Hardware black cutoff for red shadows. |
| `0x6E` | **Video Black Level (Green)** | Hardware black cutoff for green shadows. |
| `0x70` | **Video Black Level (Blue)** | Hardware black cutoff for blue shadows. |
| `0x60` | **Input Select** | Switch video input source (DP 1, DP 2, HDMI 1, HDMI 2, Type-C). |
| `0xDF` | **VCP Version** | Read supported VESA MCCS version from display firmware. |

### 3.2. Windows Win32 Low-Level Access (`dxva2.dll`)
On Windows, physical monitor handles and VCP registers are queried without external third-party drivers via:
- `user32.EnumDisplayMonitors` $\rightarrow$ obtain `HMONITOR`.
- `dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR` $\rightarrow$ retrieve physical monitor count.
- `dxva2.GetPhysicalMonitorsFromHMONITOR` $\rightarrow$ obtain `HANDLE hPhysicalMonitor`.
- `dxva2.GetVCPFeatureAndVCPFeatureReply(hPhysicalMonitor, vcpCode, ...)` $\rightarrow$ read current and max values.
- `dxva2.SetVCPFeature(hPhysicalMonitor, vcpCode, newValue)` $\rightarrow$ write hardware register directly.
- `dxva2.DestroyPhysicalMonitors` $\rightarrow$ clean up resources.

---

## 4. Open-Source Ecosystem & Software Tooling

### 4.1. Calibration, LUT & Profile Repositories
- **DisplayCAL Python 3 (`eoyilmaz/displaycal-py3`):** Modern Python 3 frontend for ArgyllCMS. Performs full colorimeter profiling, 3D LUT generation (`.cube`), and CIEDE2000 verification reporting.
- **novideo_srgb (`ledoge/novideo_srgb`):** C# utility leveraging NVIDIA NVAPI undocumented calls to apply direct LUT-Matrix-LUT clamping on GPU hardware, with EDID chromaticity parsing and hardware dithering.
- **dwm_lut (`ledoge/dwm_lut`):** Injects 3D LUT shader into Windows Desktop Window Manager (DWM) composition pipeline using tetrahedral interpolation and blue-noise dithering.
- **MHC2Gen (`dogegenetics/mhcc`):** Generates Microsoft Hardware Calibration v2 (MHC2) ICC profiles for native Windows 10/11 DWM matrix/LUT execution without DLL injection.
- **Little CMS (`mm2/Little-CMS`):** Full ISO 15076-1 / ICC v4.4 CMM engine for ultra-fast color transformation and ICC parsing.
- **OpenColorIO (`AcademySoftwareFoundation/OpenColorIO`):** Academy / VFX standard color management system supporting full ACES workflows.

### 4.2. DDC/CI Hardware Control Repositories
- **monitorcontrol (`newAM/monitorcontrol`):** Python library for Windows & Linux DDC/CI communication.
- **Monitorian (`monitorian-ddc-ci/monitorian-brightness-control`):** Clean .NET C# architecture for EDID parsing (`EdidInfo.cs`), DDC/CI, and HDR management.
- **ddcutil (`rockowitz/ddcutil`) & MonitorControl macOS (`MonitorControl/MonitorControl`):** Linux I2C and Apple Silicon display hardware control standards.
- **colour-science (`colour-science/colour`):** Authoritative Python library for comprehensive colorimetric mathematics, CIE conversions, $\Delta E_{00}$, and chromatic adaptation (Bradford / CAT02).

### 4.3. Visual Test Patterns & Calibration Platforms
- **ArgyllCMS (`www.argyllcms.com`):** Open-source CLI calibration and profiling engine supporting hardware colorimeters/spectrophotometers.
- **The Lagom LCD Monitor Test Pages (`www.lagom.nl/lcd-test/`):**
  - *Black Level:* Differentiate RGB 1–20 from black 0 (prevents black crush).
  - *White Saturation:* Verify checkerboard visibility at RGB 251–254 (prevents white clip).
  - *Gamma 2.2 Test:* Dithered luminance grid to verify 2.2 alignment across R, G, B channels.
  - *Gradient / Banding:* Smoothness check across 256 grayscale levels.
- **EIZO Monitor Test (`www.eizo.be/monitor-test/`):** Uniformity, bad pixel, and viewing angle tests.
- **Blur Busters TestUFO (`www.testufo.com`):** Motion clarity and overshoot / inverse ghosting diagnostics.
- **RTINGS & TFTCentral:** Laboratory measurement databases with OSD gain presets, overdrive tuning tables, and reference ICC profiles.

---

## 5. Reference Literature & Standards

1. **Charles Poynton (2012):** *Digital Video and HD: Algorithms and Interfaces*, Morgan Kaufmann. (Luminance $Y$ vs Luma $Y'$, Gamma physics, Rec. 709/2020 matrix derivations, chroma subsampling).
2. **Mark D. Fairchild (2013):** *Color Appearance Models*, Wiley. (Human visual adaptation, Bradford chromatic adaptation, CIECAM02).
3. **Edward J. Giorgianni & Thomas E. Madden (2008):** *Digital Color Management: Encoding Solutions*, Wiley. (PCS, ICC architecture, gamut mapping strategies).
4. **Günter Wyszecki & W. S. Stiles (1982):** *Color Science: Concepts and Methods, Quantitative Data and Formulae*, Wiley. (CIE standard observers, spectral power distribution).
5. **G. Sharma, W. Wu, & E. N. Dalal (2005):** "The CIEDE2000 color-difference formula: Implementation notes, supplementary test data, and mathematical observations", *Color Research & Application*, 30(1), pp. 21–30.
6. **D. L. MacAdam (1942):** "Visual sensitivities to color differences in daylight", *JOSA*, 32(5), pp. 247–274. (MacAdam Ellipses).
7. **Standards:** ISO 15076-1 / ICC.1:2022, VESA MCCS v2.2a, CIE 015:2018.
