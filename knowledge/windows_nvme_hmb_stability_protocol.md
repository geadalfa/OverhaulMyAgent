# Windows NVMe Host Memory Buffer (HMB) Stability & Controller Error Protocol

## 1. Executive Summary & Root Cause Architecture

On Windows 11 24H2 (OS Build 26100/26200+) running DRAM-less NVMe SSDs (specifically controllers such as **Maxio MAP1602 / MAP1602A**, **InnoGrit IG5236/IG5220**, and **Western Digital / SanDisk SN770 / SN580**), users frequently encounter spontaneous drive dropouts, random system stuttering, or drives disappearing entirely from Windows until a full hardware power cycle.

### The Mechanism
1. **DRAM-Less Architecture & HMB Dependency:** DRAM-less NVMe SSDs do not possess dedicated onboard LPDDR4/DDR4 DRAM for their Flash Translation Layer (FTL) mapping table. Instead, they rely on the NVMe standard feature called **Host Memory Buffer (HMB)** to allocate a slice of system RAM over the PCIe bus (typically 64 MB).
2. **Windows 11 24H2 Behavioral Regression:** In 24H2, Microsoft refactored `stornvme.sys` to aggressively request large HMB allocations (often exceeding 200 MB to 512 MB).
3. **Controller DMA Panic & Driver Timeout:** When controllers like the Maxio MAP1602 receive out-of-spec or oversized buffer requests, DMA allocation overruns occur. The controller stops responding to incoming commands.
4. **Watchdog Failure & Device Drop:** 
   - Initially, Windows issues `Event ID 129 (stornvme): Reset to device, \Device\RaidPortX, was issued.`
   - If the reset fails or times out during system startup or resume from sleep, Windows logs `Event ID 11 (stornvme): The driver detected a controller error on \Device\RaidPortX.`
   - Once Event ID 11 occurs, the storage stack ejects the NVMe device from the PCIe bus to maintain kernel integrity, rendering the drive completely invisible to the OS until a full hardware reboot.

---

## 2. Diagnostic Signatures (Event Log Forensics)

To confirm this specific failure mode, inspect the Windows System Event Log:

```powershell
Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='stornvme'} | 
    Where-Object { $_.Id -in 11, 129 } | 
    Select-Object TimeCreated, Id, LevelDisplayName, Message
```

* **Event ID 129 (Warning):** `Reset to device, \Device\RaidPortX, was issued.` (Precursor warning; indicates watchdog triggered by controller non-responsiveness).
* **Event ID 11 (Error):** `The driver detected a controller error on \Device\RaidPortX.` (Drive dropped completely from system).

---

## 3. Deterministic Remediation Protocol

### Step 1: Lock HMB Allocation to 64 MB Safe Limit (Registry Policy)

Apply the Microsoft storage stack allocation clamp via PowerShell (Run as Administrator):

```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\stornvme\Parameters\Device" `
    -Name "HMBAllocationPolicy" `
    -Value 2 `
    -PropertyType DWord `
    -Force
```

#### Policy Values:
* `2` — **Standard Safe Cap (64 MB):** Recommended. Keeps DRAM-less caching performance active while preventing buffer overflow.
* `0` — **Disable HMB Entirely:** Zero HMB allocation. Guarantees 100% stability in extreme cases, with a modest degradation in sustained random write speeds.

To verify the registry value:
```powershell
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\stornvme\Parameters\Device" -Name "HMBAllocationPolicy"
```

---

### Step 2: Disable PCIe Link State Power Management (ASPM)

Prevent the PCIe bus from putting the NVMe controller into deep low-power sleep states (L1.1 / L1.2) that can fail wake-up negotiation:

```powershell
# Set Link State Power Management to OFF for both AC and DC on current power scheme
powercfg /setacvalueindex SCHEME_CURRENT 501a4d13-42af-4429-9fd1-a8218c268e20 ee12f906-d277-404b-b6da-e5fa1a576df5 0
powercfg /setdcvalueindex SCHEME_CURRENT 501a4d13-42af-4429-9fd1-a8218c268e20 ee12f906-d277-404b-b6da-e5fa1a576df5 0
powercfg /setactive SCHEME_CURRENT
```

---

### Step 3: Hardware Thermal Invariant Check

The Maxio MAP1602 controller is engineered on a 12nm process and operates with high thermal density under sustained sequential workloads (such as LLM weight checkpoint loading or game installations):
1. **Operating Envelope:** Idle should ideally be below 55°C. Throttling occurs near 75°C–80°C. Controller lockups can occur if sustained temperatures reach 90°C.
2. **Mechanical Heatsink Requirement:** Ensure a solid metal M.2 heatsink with high-conductivity thermal pads (1.0mm–1.5mm) is seated firmly across the controller chip and NAND packages. Do not rely solely on decorative foil/graphene stickers.

---

### Step 4: Post-Incident File System Integrity Scan

Following an unexpected NVMe controller drop, execute a read-only NTFS scan to verify journal consistency:

```powershell
chkdsk <DriveLetter>: /scan
```
Ensure 0 bad sectors and clean USN journal verification before proceeding with regular workloads.
