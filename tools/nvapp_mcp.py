#!/usr/bin/env python3
"""
NVIDIA App MCP Tool & CLI Bridge
Communicates with the local NVIDIA App Model Context Protocol (MCP) server
via Streamable HTTP (http://127.0.0.1:13508/mcp) or NvAppMcpServer stdio bridge.

Author: Gemi for User
"""

import sys
import os
import json
import argparse
import subprocess
import requests

HTTP_URL = "http://127.0.0.1:13508/mcp"
STDIO_EXE = r"C:\Program Files\NVIDIA Corporation\NVIDIA App\McpServer\NvAppMcpServer.exe"
TIMEOUT_SECS = 25

def send_rpc_http(method, params=None, req_id=1):
    payload = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": method,
        "params": params or {}
    }
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(HTTP_URL, json=payload, headers=headers, timeout=TIMEOUT_SECS)
        return r.json()
    except Exception as e:
        return {"error": f"HTTP request failed: {e}"}

def send_rpc_stdio(method, params=None, req_id=1):
    if not os.path.exists(STDIO_EXE):
        return {"error": f"Stdio bridge executable not found at {STDIO_EXE}"}
    
    payload = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": method,
        "params": params or {}
    }
    try:
        p = subprocess.Popen(
            [STDIO_EXE],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        body = json.dumps(payload) + "\n"
        stdout_data, _ = p.communicate(input=body, timeout=TIMEOUT_SECS)
        if stdout_data:
            return json.loads(stdout_data.strip())
        return {"error": "No output from stdio bridge"}
    except Exception as e:
        return {"error": f"Stdio bridge error: {e}"}

def rpc_call(method, params=None):
    # Try HTTP first as it does not spawn processes
    res = send_rpc_http(method, params)
    if "error" in res and "failed" in str(res.get("error", "")):
        # Fallback to stdio
        return send_rpc_stdio(method, params)
    return res

def call_tool(name, arguments=None):
    return rpc_call("tools/call", {"name": name, "arguments": arguments or {}})

def cmd_status(args):
    print("=" * 60)
    print(" NVIDIA APP RUNTIME & MCP STATUS")
    print("=" * 60)

    # 1. Driver
    d_res = call_tool("nvapp_client_get_driver_status")
    d_info = d_res.get("result", {}).get("structuredContent", {})
    if d_info:
        driver = d_info.get("installedDriver", {})
        print(f"GPU Driver      : Version {driver.get('version')} ({driver.get('channel')})")
        print(f"System Type     : {d_info.get('systemType')}")
        rec = d_info.get("recommendedDrivers", [])
        if rec:
            print(f"Updates Avail   : Yes ({rec[0].get('version')})")
        else:
            print("Updates Avail   : Up to date (No new driver pending)")
    else:
        print("Driver Status   : Unable to query")

    # 2. Overlay
    o_res = call_tool("nvapp_overlay_get_status")
    o_info = o_res.get("result", {}).get("structuredContent", {})
    if o_info:
        print(f"Overlay View    : {o_info.get('overlayView')}")
        print(f"Recording       : {'ACTIVE' if o_info.get('recordingActive') else 'Idle'}")
        print(f"Instant Replay  : {'Enabled' if o_info.get('instantReplayEnabled') else 'Disabled'}")
        print(f"Perf HUD Stats  : {'Visible' if o_info.get('statsOverlayEnabled') else 'Hidden'}")
        print(f"RTX Dynamic Vib : {'Enabled' if o_info.get('rtxDvc') else 'Disabled'}")
        print(f"RTX HDR         : {'Enabled' if o_info.get('rtxHdr') else 'Disabled'}")
    
    # 3. Game
    g_res = call_tool("nvapp_overlay_get_current_game_info")
    g_info = g_res.get("result", {}).get("structuredContent", {})
    if g_info and g_info.get("running"):
        print(f"Active Game     : {g_info.get('gameName')} (PID: {g_info.get('processId')}, Fullscreen: {g_info.get('fullscreen')})")
    else:
        print("Active Game     : None currently running")

    # 4. Notebook features
    l_res = call_tool("nvapp_client_get_laptop_features")
    l_info = l_res.get("result", {}).get("structuredContent", {})
    if l_info:
        bb = l_info.get("batteryBoost", {})
        wm = l_info.get("whisperMode", {})
        if bb.get("supported"):
            print(f"Battery Boost   : {'Enabled' if bb.get('enabled') else 'Disabled'} ({bb.get('frameRate')} FPS)")
        if wm.get("supported"):
            print(f"Whisper Mode    : {'Enabled' if wm.get('enabled') else 'Disabled'} ({wm.get('fanVolume')})")
    print("=" * 60)

def cmd_apps(args):
    print("Scanning discovered applications and games via NVIDIA App MCP...")
    res = call_tool("nvapp_client_get_applications")
    apps = res.get("result", {}).get("structuredContent", {}).get("applications", [])
    if not apps:
        print("No applications found or query timed out.")
        return

    print(f"\nFound {len(apps)} applications:")
    print(f"{'No.':<4} {'Display Name':<35} {'OPS':<6} {'AC State':<12} {'Available Presets'}")
    print("-" * 80)
    for idx, a in enumerate(apps, 1):
        name = a.get("displayName", "Unknown")[:34]
        ops = "Yes" if a.get("opsSupported") else "No"
        ac = a.get("optimizationProfiles", {}).get("ac", {})
        state = ac.get("currentState", "N/A")
        presets = ", ".join(ac.get("availablePresets", [])) or "None"
        print(f"{idx:<4} {name:<35} {ops:<6} {state:<12} {presets}")

def cmd_optimize(args):
    game = args.game
    preset = args.preset
    power = args.power or "AC"
    print(f"Applying preset '{preset}' to '{game}' (Power: {power})...")
    res = call_tool("nvapp_client_set_game_optimization", {
        "game": game,
        "preset": preset,
        "powerSource": power
    })
    
    if "result" in res:
        text = res["result"].get("content", [{}])[0].get("text", "")
        print("Result:", text or "Success")
    else:
        print("Error:", res.get("error", "Unknown error"))

def cmd_overlay(args):
    if args.stats is not None:
        val = args.stats.lower() in ("true", "1", "on", "yes")
        print(f"Setting stats overlay to {val}...")
        res = call_tool("nvapp_overlay_configure_stats", {"enable": val})
        print(res.get("result", {}).get("content", [{}])[0].get("text", "Done"))

    if args.dvc is not None:
        val = args.dvc.lower() in ("true", "1", "on", "yes")
        print(f"Setting RTX Dynamic Vibrance filter to {val}...")
        res = call_tool("nvapp_overlay_configure_filters", {"filter": "rtx_dvc", "enable": val})
        print(res.get("result", {}).get("content", [{}])[0].get("text", "Done"))

    if args.record is not None:
        val = args.record.lower() in ("true", "1", "on", "yes")
        print(f"Setting recording active={val}...")
        res = call_tool("nvapp_overlay_capture", {"action": "toggle_recording", "enable": val})
        print(res.get("result", {}).get("content", [{}])[0].get("text", "Done"))

    if args.screenshot:
        print("Capturing screenshot via NVIDIA App...")
        res = call_tool("nvapp_overlay_capture", {"action": "capture_screenshot"})
        print(res.get("result", {}).get("content", [{}])[0].get("text", "Done"))

def cmd_driver(args):
    print("NVIDIA Driver Status & Highlights:")
    d_res = call_tool("nvapp_client_get_driver_status")
    print(d_res.get("result", {}).get("content", [{}])[0].get("text", ""))

    print("\nRelease Notes Abstract:")
    r_res = call_tool("nvapp_client_get_driver_release_notes", {"driver": "INSTALLED"})
    print(r_res.get("result", {}).get("content", [{}])[0].get("text", ""))

def cmd_tools(args):
    res = rpc_call("tools/list")
    tools = res.get("result", {}).get("tools", [])
    print(f"NVIDIA App MCP Server exposes {len(tools)} tools:\n")
    for t in tools:
        print(f"• {t['name']}")
        print(f"  Description : {t.get('description', '')}")
        props = list(t.get("inputSchema", {}).get("properties", {}).keys())
        if props:
            print(f"  Parameters  : {', '.join(props)}")
        print()

def main():
    parser = argparse.ArgumentParser(description="NVIDIA App MCP Client & Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # status
    subparsers.add_parser("status", help="Show NVIDIA App runtime, driver, and overlay status")

    # apps
    subparsers.add_parser("apps", help="List discovered games and optimization states")

    # optimize
    opt_p = subparsers.add_parser("optimize", help="Apply game optimization preset")
    opt_p.add_argument("--game", required=True, help="Game or application name")
    opt_p.add_argument("--preset", required=True, choices=["Balanced", "Performance", "Recommended", "Quality", "Revert"], help="Preset")
    opt_p.add_argument("--power", choices=["AC", "Battery"], default="AC", help="Power profile")

    # overlay
    ov_p = subparsers.add_parser("overlay", help="Manage overlay, performance stats, and capture")
    ov_p.add_argument("--stats", choices=["on", "off"], help="Show/hide performance statistics HUD")
    ov_p.add_argument("--dvc", choices=["on", "off"], help="Toggle RTX Dynamic Vibrance")
    ov_p.add_argument("--record", choices=["on", "off"], help="Start/stop recording")
    ov_p.add_argument("--screenshot", action="store_true", help="Take a screenshot")

    # driver
    subparsers.add_parser("driver", help="Get driver version and release highlights")

    # tools
    subparsers.add_parser("tools", help="List all available MCP tools and schemas")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "status":
        cmd_status(args)
    elif args.command == "apps":
        cmd_apps(args)
    elif args.command == "optimize":
        cmd_optimize(args)
    elif args.command == "overlay":
        cmd_overlay(args)
    elif args.command == "driver":
        cmd_driver(args)
    elif args.command == "tools":
        cmd_tools(args)

if __name__ == "__main__":
    main()
