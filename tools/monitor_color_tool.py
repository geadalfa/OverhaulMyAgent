#!/usr/bin/env python3
"""
monitor_color_tool.py
Display Colorimetry, EDID Analysis, DDC/CI VESA MCCS Hardware Control,
and CIEDE2000 Accuracy Evaluation Tool for Windows & macOS.

Author: Gemi (for User)
Built with Zero-External-Dependency architecture (pure Python + Windows Win32 dxva2 / macOS APIs).
"""

import argparse
import ctypes
from ctypes import wintypes
import json
import math
import os
import sys

# Windows CP1252 terminal safe encoding
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ==============================================================================
# 1. CIEDE2000 (ΔE00) Color Difference Engine (Sharma et al. 2005)
# ==============================================================================

def ciede2000(lab1, lab2, kL=1.0, kC=1.0, kH=1.0):
    """
    Computes CIEDE2000 Delta E between two CIELAB colors (L*, a*, b*).
    Follows Gaurav Sharma, Wencheng Wu, Edul N. Dalal (2005).
    """
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2

    # Step 1: Calculate C1, C2, C_bar, G
    C1 = math.hypot(a1, b1)
    C2 = math.hypot(a2, b2)
    C_bar = (C1 + C2) / 2.0
    C_bar_pow7 = C_bar ** 7
    G = 0.5 * (1.0 - math.sqrt(C_bar_pow7 / (C_bar_pow7 + 6103515625.0))) # 25^7 = 6103515625

    a1_prime = (1.0 + G) * a1
    a2_prime = (1.0 + G) * a2
    C1_prime = math.hypot(a1_prime, b1)
    C2_prime = math.hypot(a2_prime, b2)

    # Hue angles in degrees [0, 360)
    def compute_hue_deg(a_p, b):
        if a_p == 0 and b == 0:
            return 0.0
        deg = math.degrees(math.atan2(b, a_p))
        return deg + 360.0 if deg < 0 else deg

    h1_prime = compute_hue_deg(a1_prime, b1)
    h2_prime = compute_hue_deg(a2_prime, b2)

    # Step 2: Calculate Delta L', Delta C', Delta H'
    delta_L_prime = L2 - L1
    delta_C_prime = C2_prime - C1_prime

    if C1_prime * C2_prime == 0.0:
        delta_h_prime = 0.0
    else:
        diff_h = h2_prime - h1_prime
        if abs(diff_h) <= 180.0:
            delta_h_prime = diff_h
        elif diff_h > 180.0:
            delta_h_prime = diff_h - 360.0
        else:
            delta_h_prime = diff_h + 360.0

    delta_H_prime = 2.0 * math.sqrt(C1_prime * C2_prime) * math.sin(math.radians(delta_h_prime / 2.0))

    # Step 3: Calculate CIEDE2000 total color difference
    L_bar_prime = (L1 + L2) / 2.0
    C_bar_prime = (C1_prime + C2_prime) / 2.0

    if C1_prime * C2_prime == 0.0:
        h_bar_prime = h1_prime + h2_prime
    else:
        abs_diff_h = abs(h1_prime - h2_prime)
        sum_h = h1_prime + h2_prime
        if abs_diff_h <= 180.0:
            h_bar_prime = sum_h / 2.0
        elif sum_h < 360.0:
            h_bar_prime = (sum_h + 360.0) / 2.0
        else:
            h_bar_prime = (sum_h - 360.0) / 2.0

    T = (1.0 - 0.17 * math.cos(math.radians(h_bar_prime - 30.0))
             + 0.24 * math.cos(math.radians(2.0 * h_bar_prime))
             + 0.32 * math.cos(math.radians(3.0 * h_bar_prime + 6.0))
             - 0.20 * math.cos(math.radians(4.0 * h_bar_prime - 63.0)))

    delta_theta = 30.0 * math.exp(-(((h_bar_prime - 275.0) / 25.0) ** 2))
    C_bar_prime_pow7 = C_bar_prime ** 7
    R_C = 2.0 * math.sqrt(C_bar_prime_pow7 / (C_bar_prime_pow7 + 6103515625.0))
    R_T = -math.sin(math.radians(2.0 * delta_theta)) * R_C

    L_bar_minus_50_sq = (L_bar_prime - 50.0) ** 2
    S_L = 1.0 + ((0.015 * L_bar_minus_50_sq) / math.sqrt(20.0 + L_bar_minus_50_sq))
    S_C = 1.0 + 0.045 * C_bar_prime
    S_H = 1.0 + 0.015 * C_bar_prime * T

    dL_term = delta_L_prime / (kL * S_L)
    dC_term = delta_C_prime / (kC * S_C)
    dH_term = delta_H_prime / (kH * S_H)

    delta_E_sq = (dL_term ** 2) + (dC_term ** 2) + (dH_term ** 2) + (R_T * dC_term * dH_term)
    return math.sqrt(max(0.0, delta_E_sq))


def evaluate_delta_e_rating(de):
    if de < 1.0:
        return "Reference Grade (Imperceptible difference to trained eye)"
    elif de <= 2.0:
        return "Professional Grade (Design & Color Grading standard tolerance)"
    elif de <= 3.0:
        return "Consumer Acceptable (Minor visible difference upon scrutiny)"
    else:
        return "Inaccurate (Noticeable color error, recalibration strongly advised)"


# ==============================================================================
# 2. EDID Parsing & Chromaticity Triangle Engine
# ==============================================================================

STANDARD_GAMUTS = {
    "sRGB": {
        "red": (0.6400, 0.3300),
        "green": (0.3000, 0.6000),
        "blue": (0.1500, 0.0600),
        "white": (0.3127, 0.3290)
    },
    "DCI-P3": {
        "red": (0.6800, 0.3200),
        "green": (0.2650, 0.6900),
        "blue": (0.1500, 0.0600),
        "white": (0.3127, 0.3290)
    },
    "Adobe RGB": {
        "red": (0.6400, 0.3300),
        "green": (0.2100, 0.7100),
        "blue": (0.1500, 0.0600),
        "white": (0.3127, 0.3290)
    },
    "Rec. 2020": {
        "red": (0.7080, 0.2920),
        "green": (0.1700, 0.7970),
        "blue": (0.1310, 0.0460),
        "white": (0.3127, 0.3290)
    }
}

def triangle_area_2d(p1, p2, p3):
    return 0.5 * abs(p1[0]*(p2[1] - p3[1]) + p2[0]*(p3[1] - p1[1]) + p3[0]*(p1[1] - p2[1]))

def parse_edid_block(edid_bytes):
    """
    Parses VESA EDID binary block (128 bytes minimum).
    """
    if len(edid_bytes) < 128:
        return None
    if edid_bytes[:8] != b'\x00\xff\xff\xff\xff\xff\xff\x00':
        return None

    # Manufacturer ID (compressed 3 letters in bytes 8-9)
    m_id = (edid_bytes[8] << 8) | edid_bytes[9]
    c1 = chr(((m_id >> 10) & 0x1F) + 64)
    c2 = chr(((m_id >> 5) & 0x1F) + 64)
    c3 = chr((m_id & 0x1F) + 64)
    mfg = f"{c1}{c2}{c3}"
    prod_code = edid_bytes[10] | (edid_bytes[11] << 8)
    serial_no = (edid_bytes[12] | (edid_bytes[13] << 8) |
                 (edid_bytes[14] << 16) | (edid_bytes[15] << 24))

    # Gamma (Byte 23)
    gamma = (edid_bytes[23] + 100) / 100.0 if edid_bytes[23] != 0xFF else None

    # Chromaticity coordinates (Bytes 25-34)
    b25, b26 = edid_bytes[25], edid_bytes[26]
    rx = ((edid_bytes[27] << 2) | ((b25 >> 6) & 0x3)) / 1024.0
    ry = ((edid_bytes[28] << 2) | ((b25 >> 4) & 0x3)) / 1024.0
    gx = ((edid_bytes[29] << 2) | ((b25 >> 2) & 0x3)) / 1024.0
    gy = ((edid_bytes[30] << 2) | (b25 & 0x3)) / 1024.0
    bx = ((edid_bytes[31] << 2) | ((b26 >> 6) & 0x3)) / 1024.0
    by = ((edid_bytes[32] << 2) | ((b26 >> 4) & 0x3)) / 1024.0
    wx = ((edid_bytes[33] << 2) | ((b26 >> 2) & 0x3)) / 1024.0
    wy = ((edid_bytes[34] << 2) | (b26 & 0x3)) / 1024.0

    # Descriptor blocks (Bytes 54, 72, 90, 108)
    monitor_name = ""
    for offset in (54, 72, 90, 108):
        block = edid_bytes[offset:offset+18]
        if block[:4] == b'\x00\x00\x00\xfc': # Name descriptor
            monitor_name = block[5:].decode('ascii', errors='ignore').split('\n')[0].strip()

    # Calculate triangle area and gamut coverage ratios
    r_pt, g_pt, b_pt = (rx, ry), (gx, gy), (bx, by)
    panel_area = triangle_area_2d(r_pt, g_pt, b_pt)
    srgb_area = triangle_area_2d(STANDARD_GAMUTS["sRGB"]["red"], STANDARD_GAMUTS["sRGB"]["green"], STANDARD_GAMUTS["sRGB"]["blue"])
    dcip3_area = triangle_area_2d(STANDARD_GAMUTS["DCI-P3"]["red"], STANDARD_GAMUTS["DCI-P3"]["green"], STANDARD_GAMUTS["DCI-P3"]["blue"])
    adobe_area = triangle_area_2d(STANDARD_GAMUTS["Adobe RGB"]["red"], STANDARD_GAMUTS["Adobe RGB"]["green"], STANDARD_GAMUTS["Adobe RGB"]["blue"])

    is_wide_gamut = (panel_area / srgb_area) > 1.15

    return {
        "manufacturer": mfg,
        "product_code": hex(prod_code),
        "serial_number": serial_no if serial_no > 0 else "N/A",
        "name": monitor_name or f"{mfg} {hex(prod_code)}",
        "gamma": gamma,
        "primaries": {
            "red": (round(rx, 4), round(ry, 4)),
            "green": (round(gx, 4), round(gy, 4)),
            "blue": (round(bx, 4), round(by, 4)),
            "white": (round(wx, 4), round(wy, 4))
        },
        "gamut_metrics": {
            "panel_cie1931_area": round(panel_area, 5),
            "sRGB_volume_percent": round((panel_area / srgb_area) * 100.0, 1),
            "DCI_P3_volume_percent": round((panel_area / dcip3_area) * 100.0, 1),
            "Adobe_RGB_volume_percent": round((panel_area / adobe_area) * 100.0, 1),
            "is_wide_gamut": is_wide_gamut,
            "clamping_required_for_sdr": is_wide_gamut
        }
    }

def get_windows_registry_edids():
    """Reads all EDID binary blocks from Windows Registry."""
    import winreg
    results = []
    base_path = r"SYSTEM\CurrentControlSet\Enum\DISPLAY"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_path) as k_display:
            i = 0
            while True:
                try:
                    device_id = winreg.EnumKey(k_display, i)
                    i += 1
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{base_path}\\{device_id}") as k_device:
                        j = 0
                        while True:
                            try:
                                inst_id = winreg.EnumKey(k_device, j)
                                j += 1
                                dp_path = f"{base_path}\\{device_id}\\{inst_id}\\Device Parameters"
                                try:
                                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, dp_path) as k_dp:
                                        edid_bytes, _ = winreg.QueryValueEx(k_dp, "EDID")
                                        parsed = parse_edid_block(edid_bytes)
                                        if parsed:
                                            parsed["registry_path"] = f"{device_id}\\{inst_id}"
                                            results.append(parsed)
                                except OSError:
                                    pass
                            except OSError:
                                break
                except OSError:
                    break
    except OSError:
        pass
    return results


# ==============================================================================
# 3. DDC/CI Hardware VCP Engine (Windows dxva2.dll)
# ==============================================================================

VCP_REGISTERS = {
    0x10: ("Brightness", "Luminance intensity"),
    0x12: ("Contrast", "Video signal contrast"),
    0x14: ("ColorPreset", "Color temperature preset"),
    0x16: ("RedGain", "Video Gain Red"),
    0x18: ("GreenGain", "Video Gain Green"),
    0x1A: ("BlueGain", "Video Gain Blue"),
    0x6C: ("RedBlackLevel", "Video Black Level Red"),
    0x6E: ("GreenBlackLevel", "Video Black Level Green"),
    0x70: ("BlueBlackLevel", "Video Black Level Blue"),
    0x60: ("InputSelect", "Active video input source"),
    0xDF: ("VcpVersion", "VESA MCCS protocol version")
}

class PHYSICAL_MONITOR(ctypes.Structure):
    _fields_ = [
        ('hPhysicalMonitor', wintypes.HANDLE),
        ('szPhysicalMonitorDescription', wintypes.WCHAR * 128)
    ]

def get_windows_physical_monitors():
    """Returns list of active physical monitor descriptors and handles via dxva2.dll."""
    if os.name != 'nt':
        return []

    user32 = ctypes.windll.user32
    dxva2 = ctypes.windll.dxva2

    hmonitors = []
    def _enum_proc(hmon, hdc, lprect, lparam):
        hmonitors.append(hmon)
        return True

    MONITORENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
    user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(_enum_proc), 0)

    results = []
    for hmon in hmonitors:
        count = wintypes.DWORD()
        if dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(hmon, ctypes.byref(count)):
            phys_array = (PHYSICAL_MONITOR * count.value)()
            if dxva2.GetPhysicalMonitorsFromHMONITOR(hmon, count.value, phys_array):
                for p in phys_array:
                    results.append({
                        "hmonitor": hmon,
                        "hPhysicalMonitor": p.hPhysicalMonitor,
                        "description": str(p.szPhysicalMonitorDescription),
                        "count_for_hmon": count.value,
                        "raw_array": phys_array
                    })
    return results

def query_physical_monitor_vcp(handle, vcp_code):
    """Queries a single VCP register value and max value."""
    dxva2 = ctypes.windll.dxva2
    cur = wintypes.DWORD()
    maximum = wintypes.DWORD()
    success = dxva2.GetVCPFeatureAndVCPFeatureReply(handle, vcp_code, None, ctypes.byref(cur), ctypes.byref(maximum))
    if success:
        return cur.value, maximum.value
    return None, None

def set_physical_monitor_vcp(handle, vcp_code, new_val):
    """Sets a VCP register value."""
    dxva2 = ctypes.windll.dxva2
    success = dxva2.SetVCPFeature(handle, vcp_code, new_val)
    return bool(success)


# ==============================================================================
# 4. Command Handlers
# ==============================================================================

def cmd_audit(args):
    edids = get_windows_registry_edids() if os.name == 'nt' else []
    phys_mons = get_windows_physical_monitors() if os.name == 'nt' else []

    audit_data = {
        "os": os.name,
        "edid_displays_detected": len(edids),
        "physical_ddc_monitors_detected": len(phys_mons),
        "displays": []
    }

    # Deduplicate EDIDs by name/product_code
    seen_edids = set()
    unique_edids = []
    for e in edids:
        key = (e["name"], e["product_code"])
        if key not in seen_edids:
            seen_edids.add(key)
            unique_edids.append(e)

    for idx, p in enumerate(phys_mons):
        disp_info = {
            "index": idx,
            "description": p["description"],
            "vcp_registers": {}
        }
        for code, (name, desc) in VCP_REGISTERS.items():
            cur, max_val = query_physical_monitor_vcp(p["hPhysicalMonitor"], code)
            if cur is not None:
                disp_info["vcp_registers"][f"0x{code:02X}_{name}"] = {
                    "code": f"0x{code:02X}",
                    "current": cur,
                    "max": max_val,
                    "description": desc
                }
        audit_data["displays"].append(disp_info)

    if args.json:
        print(json.dumps({"audit": audit_data, "edid_profiles": unique_edids}, indent=2))
        return

    print("================================================================================")
    print(" DISPLAY HARDWARE & COLORIMETRY AUDIT REPORT")
    print("================================================================================")
    print(f"Detected Physical Monitors (DDC/CI): {len(phys_mons)}")
    for d in audit_data["displays"]:
        print(f"\n[Monitor #{d['index']}] {d['description']}")
        print("  Current Hardware Registers (VESA MCCS):")
        for k, reg in d["vcp_registers"].items():
            print(f"    - {reg['code']} {k.split('_')[1]:<15}: {reg['current']:>3} / {reg['max']:<3} ({reg['description']})")

    print(f"\nDetected EDID Profiles (Registry): {len(unique_edids)}")
    for e in unique_edids:
        print(f"\n[EDID Profile] {e['name']} ({e['manufacturer']} - {e['product_code']})")
        print(f"  Gamma: {e['gamma']}")
        print(f"  Primaries: Red {e['primaries']['red']}, Green {e['primaries']['green']}, Blue {e['primaries']['blue']}, White {e['primaries']['white']}")
        gm = e["gamut_metrics"]
        print(f"  Gamut Coverage: {gm['sRGB_volume_percent']}% sRGB, {gm['DCI_P3_volume_percent']}% DCI-P3, {gm['Adobe_RGB_volume_percent']}% Adobe RGB")
        if gm["is_wide_gamut"]:
            print("  [!] Wide-Gamut Display Detected: Clamping recommended for SDR to avoid oversaturation.")
        else:
            print("  [OK] Standard Gamut Display: Clamping not required.")


def cmd_edid(args):
    edids = get_windows_registry_edids() if os.name == 'nt' else []
    if args.json:
        print(json.dumps(edids, indent=2))
        return

    for e in edids:
        print("--------------------------------------------------------------------------------")
        print(f"Monitor: {e['name']} ({e['manufacturer']} {e['product_code']})")
        print(f"Serial : {e['serial_number']}")
        print(f"Gamma  : {e['gamma']}")
        print("Chromaticity Coordinates (CIE 1931 xy):")
        for color, coord in e["primaries"].items():
            print(f"  {color.capitalize():<6}: x={coord[0]:.4f}, y={coord[1]:.4f}")
        gm = e["gamut_metrics"]
        print("Gamut Metrics:")
        print(f"  CIE 1931 Triangle Area: {gm['panel_cie1931_area']}")
        print(f"  sRGB Volume Ratio     : {gm['sRGB_volume_percent']}%")
        print(f"  DCI-P3 Volume Ratio   : {gm['DCI_P3_volume_percent']}%")
        print(f"  Adobe RGB Ratio       : {gm['Adobe_RGB_volume_percent']}%")
        print(f"  Wide-Gamut Panel      : {'YES' if gm['is_wide_gamut'] else 'NO'}")
        print(f"  SDR Clamping Required : {'YES' if gm['clamping_required_for_sdr'] else 'NO'}")


def cmd_vcp_get(args):
    phys_mons = get_windows_physical_monitors() if os.name == 'nt' else []
    if not phys_mons:
        sys.stderr.write("Error: No physical monitors with DDC/CI access detected.\n")
        sys.exit(1)

    if args.monitor >= len(phys_mons):
        sys.stderr.write(f"Error: Monitor index {args.monitor} out of range (found {len(phys_mons)}).\n")
        sys.exit(1)

    target_mon = phys_mons[args.monitor]
    results = {}

    vcp_list = [int(args.code, 16)] if args.code else VCP_REGISTERS.keys()
    for code in vcp_list:
        name = VCP_REGISTERS.get(code, ("Unknown", ""))[0]
        cur, max_val = query_physical_monitor_vcp(target_mon["hPhysicalMonitor"], code)
        if cur is not None:
            results[f"0x{code:02X}_{name}"] = {"current": cur, "max": max_val}

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"VCP Registers for Monitor #{args.monitor} [{target_mon['description']}]:")
        for k, v in results.items():
            print(f"  {k:<20}: {v['current']} / {v['max']}")


def cmd_vcp_set(args):
    phys_mons = get_windows_physical_monitors() if os.name == 'nt' else []
    if not phys_mons:
        sys.stderr.write("Error: No physical monitors detected.\n")
        sys.exit(1)

    if args.monitor >= len(phys_mons):
        sys.stderr.write(f"Error: Monitor index {args.monitor} out of range.\n")
        sys.exit(1)

    target_mon = phys_mons[args.monitor]
    code = int(args.code, 16)
    val = args.value

    # Invariant checks:
    # Red (0x16), Green (0x18), Blue (0x1A) Gain must never exceed 100
    if code in (0x16, 0x18, 0x1A) and val > 100:
        sys.stderr.write("INVARIANT VIOLATION: RGB Gain must never be increased above 100 (factory default). Attenuate excess channels downward to prevent clipping.\n")
        sys.exit(1)

    cur, max_val = query_physical_monitor_vcp(target_mon["hPhysicalMonitor"], code)
    if max_val and val > max_val:
        sys.stderr.write(f"Error: Target value {val} exceeds monitor reported maximum {max_val}.\n")
        sys.exit(1)

    success = set_physical_monitor_vcp(target_mon["hPhysicalMonitor"], code, val)
    if success:
        print(f"Successfully set VCP 0x{code:02X} on Monitor #{args.monitor} [{target_mon['description']}] to {val}.")
    else:
        sys.stderr.write(f"Failed to set VCP 0x{code:02X} to {val}. Hardware rejected the write command.\n")
        sys.exit(1)


def cmd_delta_e(args):
    try:
        t_l, t_a, t_b = [float(x.strip()) for x in args.target_lab.split(",")]
        s_l, s_a, s_b = [float(x.strip()) for x in args.sample_lab.split(",")]
    except Exception as e:
        sys.stderr.write(f"Error parsing Lab coordinates: {e}. Format must be 'L,a,b' (e.g. '50.0,0.0,0.0')\n")
        sys.exit(1)

    de = ciede2000((t_l, t_a, t_b), (s_l, s_a, s_b))
    rating = evaluate_delta_e_rating(de)

    res = {
        "target_lab": [t_l, t_a, t_b],
        "sample_lab": [s_l, s_a, s_b],
        "delta_e_00": round(de, 4),
        "rating": rating,
        "is_studio_reference": de < 1.0,
        "is_design_acceptable": de <= 2.0
    }

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print("--------------------------------------------------------------------------------")
        print(" CIEDE2000 (ΔE00) COLOR DIFFERENCE EVALUATION")
        print("--------------------------------------------------------------------------------")
        print(f"Target Lab : L*={t_l:.2f}, a*={t_a:.2f}, b*={t_b:.2f}")
        print(f"Sample Lab : L*={s_l:.2f}, a*={s_a:.2f}, b*={s_b:.2f}")
        print(f"Delta E 00 : {res['delta_e_00']}")
        print(f"Evaluation : {res['rating']}")


# ==============================================================================
# 5. CLI Router
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Zero-Dependency Display Colorimetry & DDC/CI Hardware Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # audit
    p_audit = subparsers.add_parser("audit", help="Full hardware, EDID, and VCP registers audit")
    p_audit.add_argument("--json", action="store_true", help="Output in structured JSON format")

    # edid
    p_edid = subparsers.add_parser("edid", help="Decode EDID blocks from OS registry")
    p_edid.add_argument("--json", action="store_true", help="Output in structured JSON format")

    # vcp-get
    p_vcp_get = subparsers.add_parser("vcp-get", help="Read physical monitor VCP register")
    p_vcp_get.add_argument("--monitor", type=int, default=0, help="Monitor index (default: 0)")
    p_vcp_get.add_argument("--code", type=str, default=None, help="Hex VCP code (e.g. 0x10)")
    p_vcp_get.add_argument("--json", action="store_true", help="Output in structured JSON format")

    # vcp-set
    p_vcp_set = subparsers.add_parser("vcp-set", help="Write physical monitor VCP register")
    p_vcp_set.add_argument("--monitor", type=int, default=0, help="Monitor index (default: 0)")
    p_vcp_set.add_argument("--code", type=str, required=True, help="Hex VCP code (e.g. 0x10)")
    p_vcp_set.add_argument("--value", type=int, required=True, help="Value to set")

    # delta-e
    p_de = subparsers.add_parser("delta-e", help="Compute CIEDE2000 color difference")
    p_de.add_argument("--target-lab", type=str, required=True, help="Target L*,a*,b* (comma separated)")
    p_de.add_argument("--sample-lab", type=str, required=True, help="Sample L*,a*,b* (comma separated)")
    p_de.add_argument("--json", action="store_true", help="Output in structured JSON format")

    args = parser.parse_args()

    if args.command == "audit":
        cmd_audit(args)
    elif args.command == "edid":
        cmd_edid(args)
    elif args.command == "vcp-get":
        cmd_vcp_get(args)
    elif args.command == "vcp-set":
        cmd_vcp_set(args)
    elif args.command == "delta-e":
        cmd_delta_e(args)


if __name__ == "__main__":
    main()
