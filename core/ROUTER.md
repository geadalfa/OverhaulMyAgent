# Progressive Disclosure & Skill Dispatch Router

Use this table to look up specialized knowledge, skills, or tools on demand. Do NOT load all files at boot. Read only the specific target file required for the active user prompt.

| User Intent / Trigger | Dedicated Skill / Knowledge | Deterministic Tool | Primary Target File |
| :--- | :--- | :--- | :--- |
| **Code Planning / Refactoring (>2 files)** | `skills/plan-first/` | Built-in | `skills/plan-first/SKILL.md` |
| **Debugging / Crash / Test Failure** | `skills/systematic-debugging/` | Built-in | `skills/systematic-debugging/SKILL.md` |
| **API Contract / Spec-Driven Feature** | `skills/spec-driven-development/` | `tools/openspec_tool.py` | `skills/spec-driven-development/SKILL.md` |
| **UI/UX Design / Component Styling** | `skills/anti-slop-ui-design/` | Built-in | `skills/anti-slop-ui-design/SKILL.md` |
| **Technical Writing / PR Microcopy** | `skills/human-technical-writing/` | `tools/corporate_firewall.py` | `skills/human-technical-writing/SKILL.md` |
| **Corporate Communication / Escalation** | `skills/corporate-diplomacy-and-career-acceleration/` | `tools/corporate_firewall.py` | `skills/corporate-diplomacy-and-career-acceleration/SKILL.md` |
| **Financial Math / Waterfall / Debt / Portfolio** | `skills/holistic-financial-advisor/` | `tools/financial_calculator.py` | `tools/financial_calculator.py` |
| **ETF / Macroeconomic Analysis** | `skills/financial-etf-advisory/` | `tools/financial_calculator.py` | `skills/financial-etf-advisory/SKILL.md` |
| **Web Content Extraction / URL Ingestion** | `knowledge/web_content_extraction_protocol.md` | `tools/fetch_web.py` | `tools/fetch_web.py` |
| **Document OCR / PDF Conversion** | `skills/document-ocr-and-conversion/` | `tools/doc_converter.py` | `tools/doc_converter.py` |
| **Apple Silicon Vision OCR** | `skills/document-ocr-and-conversion/` | `tools/macos-ocr.swift` | `tools/macos-ocr.swift` |
| **Monitor Color / Calibration / DDC-CI** | `skills/display-color-calibration/` | `tools/monitor_color_tool.py` | `tools/monitor_color_tool.py` |
| **Game Modding / Nexus Safety Engine** | `skills/automated-game-modding/` | `tools/game_mod_tool.py` | `tools/game_mod_tool.py` |
| **Game Optimization / Zero-Nausea Ergonomics** | `skills/windows-gaming-optimizer/` | `tools/nvapp_mcp.py` | `core/MOTION_COMFORT_STANDARDS.md` |
| **Local LLM Ablation / Weight Steering** | `skills/llm-weight-ablation-and-steering/` | `knowledge/heretic_llm_abliteration_and_steering.md` | `skills/llm-weight-ablation-and-steering/SKILL.md` |
| **Binary / ASAR / App Reverse Engineering** | `skills/reverse-engineer-anything/` | REA MCP Server | `skills/reverse-engineer-anything/SKILL.md` |
| **Token Output Compression / RTK Proxy** | `skills/token-efficient-reconnaissance/` | `tools/rtk.py` | `tools/rtk.py` |
| **Enterprise Diagramming (C4 / Sequence / SAD)** | `skills/system-analyst-diagramming/` | `tools/confluence_drawio_tool.py` | `skills/system-analyst-diagramming/SKILL.md` |
| **Prompt Token Compression** | `skills/token-efficient-reconnaissance/` | `tools/compress_prompt.py` | `tools/compress_prompt.py` |