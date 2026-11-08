# NVIDIA App MCP Server

This MCP server interfaces directly with the local NVIDIA App on Windows, allowing AI coding and desktop assistants to inspect runtime graphics status, manage display overlays, check GPU drivers, inspect discovered games/applications, and apply Optimal Playable Settings (OPS).

## Available Capabilities
1. **Driver Insights**: Query installed GeForce / Studio driver versions, recommended drivers, rollback info (`nvapp_client_get_driver_status`, `nvapp_client_get_driver_release_notes`).
2. **Game & App Optimization**: Scan detected applications and apply performance or quality presets (`nvapp_client_get_applications`, `nvapp_client_set_game_optimization`).
3. **Overlay & Capture Controls**: Inspect overlay state, start/stop shadowplay recording, take screenshots, toggle performance HUD (`nvapp_overlay_get_status`, `nvapp_overlay_capture`, `nvapp_overlay_configure_stats`).
4. **Laptop Power & Acoustics**: On supported notebooks, read and set Whisper Mode and Battery Boost presets (`nvapp_client_get_laptop_features`, `nvapp_client_set_laptop_feature`).

## Operational Guidelines
- Before applying optimization presets with `nvapp_client_set_game_optimization`, verify with `nvapp_client_get_applications` that the target game has `opsSupported: true` and supports the requested preset (`Balanced`, `Performance`, `Recommended`, `Quality`, `Revert`).
- When querying `nvapp_client_get_applications`, specify the `game` parameter if only inspecting a single app, because scanning the entire system takes ~5-7 seconds.
- Changes to capture features or graphics settings directly modify live runtime state.
