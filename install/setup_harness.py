#!/usr/bin/env python3
"""
Interactive & Automated Multi-Harness Setup CLI for OverhaulMyAgent.
"""

import os
import sys
import shutil
import argparse

HARNESS_TARGETS = ["all", "cursor", "claude", "antigravity", "kiro", "deepseek", "chatgpt", "qoder"]

def setup(target="all", project_dir="."):
    project_dir = os.path.abspath(project_dir)
    print(f"[*] Deploying OverhaulMyAgent harness to: {project_dir}")
    print(f"[*] Target Harness: {target.upper()}")
    
    src_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Universal AGENTS.md
    shutil.copy2(os.path.join(src_root, "AGENTS.md"), os.path.join(project_dir, "AGENTS.md"))
    print("  + [✓] Installed root AGENTS.md (Open Standard)")

    if target in ["all", "cursor"]:
        shutil.copy2(os.path.join(src_root, ".cursorrules"), os.path.join(project_dir, ".cursorrules"))
        cursor_dir = os.path.join(project_dir, ".cursor", "rules")
        os.makedirs(cursor_dir, exist_ok=True)
        for f in os.listdir(os.path.join(src_root, ".cursor", "rules")):
            shutil.copy2(os.path.join(src_root, ".cursor", "rules", f), os.path.join(cursor_dir, f))
        print("  + [✓] Installed Cursor rules (.cursorrules & .cursor/rules/)")

    if target in ["all", "claude"]:
        shutil.copy2(os.path.join(src_root, "CLAUDE.md"), os.path.join(project_dir, "CLAUDE.md"))
        print("  + [✓] Installed Claude Code instructions (CLAUDE.md)")

    if target in ["all", "kiro"]:
        shutil.copy2(os.path.join(src_root, "kiro.json"), os.path.join(project_dir, "kiro.json"))
        print("  + [✓] Installed Kiro harness profile (kiro.json)")

    if target in ["all", "deepseek"]:
        shutil.copy2(os.path.join(src_root, "deepseek_harness.md"), os.path.join(project_dir, "deepseek_harness.md"))
        print("  + [✓] Installed DeepSeek/OMP harness rules (deepseek_harness.md)")

    if target in ["all", "chatgpt"]:
        shutil.copy2(os.path.join(src_root, "chatgpt_custom_instructions.md"), os.path.join(project_dir, "chatgpt_custom_instructions.md"))
        print("  + [✓] Prepared ChatGPT custom instructions (chatgpt_custom_instructions.md)")

    if target in ["all", "qoder"]:
        shutil.copy2(os.path.join(src_root, "QODER.md"), os.path.join(project_dir, "QODER.md"))
        qoder_dir = os.path.join(project_dir, ".qoder")
        os.makedirs(qoder_dir, exist_ok=True)
        print("  + [✓] Installed Qoder instructions (QODER.md & .qoder/)")
        print("        For user-scope skills/knowledge/tools run install/install_qoder.sh")

    print("\n[✓] Setup completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OverhaulMyAgent Harness Setup Tool")
    parser.add_argument("--target", choices=HARNESS_TARGETS, default="all", help="Target harness")
    parser.add_argument("--dir", default=".", help="Target project directory")
    args = parser.parse_args()
    setup(args.target, args.dir)