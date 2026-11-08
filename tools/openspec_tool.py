#!/usr/bin/env python3
"""
OpenSpec CLI Tool - Deterministic Spec-Driven Development (BRILiaN Way SDD V2)
Automates change initialization, task progress tracking, boundary validation,
decision write-back, and atomic archiving.
"""

import sys
import os
import io
import re
import argparse
from datetime import datetime
import subprocess

# Ensure utf-8 output on Windows consoles
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

OPENSPEC_BASE = "openspec"
CHANGES_DIR = os.path.join(OPENSPEC_BASE, "changes")
ARCHIVE_DIR = os.path.join(CHANGES_DIR, "archive")

PROPOSAL_TEMPLATE = """# Proposal: {name}

## Why
{why}

## What Changes
{what}
- **Mechanics / Business Logic:** 
- **Scoring / Validation:** 
- **UI / UX & Accessibility:** 
- **Asset Provenance:** Prompts and reproducible generation parameters recorded in repo.
"""

DESIGN_TEMPLATE = """# Design: {name}

## Boundaries & Contract
- **Owning Shell:** Route owner and state coordinator
- **Pluggable Module:** `{folder}`
- **Interface Contract:**
```typescript
export interface Contract {{
  onComplete: (result: {{ valueId: string; score: number }}) => void;
  onCancel: () => void;
  onError: (error: Error) => void;
}}
```

## Architecture Flow
```mermaid
flowchart LR
    Shell["Owning Shell"] --> Contract["Interface Contract"] --> Module["{name}"]
```

## Failure Scenarios & Edge Cases
1. Invalid or malformed inputs -> Reject with deterministic error before state change.
2. Unexpected cancellation -> Clean up active timer/listeners, trigger onCancel with 0 points.
3. Network / runtime failure -> Catch and route to onError handler.

## Implementation Decisions (Written Back)
- Initial specification baseline established on {date}.
"""

TASKS_TEMPLATE = """# Tasks: {name}

Done: 0 / Planned: 4

- [ ] 1. Establish directory boundary and copy/verify contracts
- [ ] 2. Implement core engine, state machine, and scoring calculations
- [ ] 3. Build UI components, user interactions, and keyboard/touch navigation
- [ ] 4. Implement unit tests with 1:1 rule-to-test parity & verify CI passes
"""

YAML_TEMPLATE = """name: {name}
target_folder: {folder}
created_at: {date}
status: active
owner: User
version: 1.0.0
"""

def ensure_dirs():
    os.makedirs(CHANGES_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

def cmd_new(args):
    ensure_dirs()
    change_name = args.name.strip().lower().replace(" ", "-")
    target_path = os.path.join(CHANGES_DIR, change_name)

    if os.path.exists(target_path):
        print(f"Error: Change specification '{change_name}' already exists at {target_path}")
        sys.exit(1)

    os.makedirs(target_path, exist_ok=True)
    os.makedirs(os.path.join(target_path, "specs"), exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    folder = args.folder or f"src/{change_name}"
    why = args.why or "Explain the problem or feature necessity here."
    what = args.what or "- Describe the primary feature addition or modification."

    with open(os.path.join(target_path, ".openspec.yaml"), "w", encoding="utf-8") as f:
        f.write(YAML_TEMPLATE.format(name=change_name, folder=folder, date=today))

    with open(os.path.join(target_path, "proposal.md"), "w", encoding="utf-8") as f:
        f.write(PROPOSAL_TEMPLATE.format(name=change_name, why=why, what=what))

    with open(os.path.join(target_path, "design.md"), "w", encoding="utf-8") as f:
        f.write(DESIGN_TEMPLATE.format(name=change_name, folder=folder, date=today))

    with open(os.path.join(target_path, "tasks.md"), "w", encoding="utf-8") as f:
        f.write(TASKS_TEMPLATE.format(name=change_name))

    with open(os.path.join(target_path, "specs", "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# Specs: {change_name}\n\nDocument concrete rules, boundary constraints, and edge-case tables here.\n")

    print(f"✓ Created OpenSpec change: '{change_name}'")
    print(f"  Location: {target_path}")
    print(f"  Artifacts: proposal.md, design.md, tasks.md, .openspec.yaml, specs/")
    print(f"  Next step: Edit proposal.md and run '/opsx-propose' or 'python openspec_tool.py status {change_name}'")

def parse_tasks(tasks_path):
    if not os.path.exists(tasks_path):
        return 0, 0, []
    
    with open(tasks_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    done = 0
    total = 0
    items = []
    task_re = re.compile(r"^\s*-\s*\[([ xX])\]\s*(.*)$")
    for line in lines:
        m = task_re.match(line)
        if m:
            total += 1
            is_done = m.group(1).lower() == "x"
            if is_done:
                done += 1
            items.append((is_done, m.group(2).strip()))
    return done, total, items

def update_tasks_count(tasks_path, done, total):
    if not os.path.exists(tasks_path):
        return
    with open(tasks_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r"Done:\s*\d+\s*/\s*Planned:\s*\d+",
        f"Done: {done} / Planned: {total}",
        content
    )
    with open(tasks_path, "w", encoding="utf-8") as f:
        f.write(new_content)

def cmd_list(args):
    ensure_dirs()
    print("================================================================================")
    print("                    OPENSPEC ACTIVE & ARCHIVED CHANGES                          ")
    print("================================================================================")

    active_changes = [
        d for d in os.listdir(CHANGES_DIR)
        if os.path.isdir(os.path.join(CHANGES_DIR, d)) and d != "archive" and not d.startswith(".")
    ]

    print("\n[ACTIVE CHANGES]")
    if not active_changes:
        print("  (None. All changes archived or none created yet.)")
    else:
        for c in sorted(active_changes):
            tasks_file = os.path.join(CHANGES_DIR, c, "tasks.md")
            done, total, _ = parse_tasks(tasks_file)
            pct = (done / total * 100) if total > 0 else 0
            bar = ("#" * int(pct // 10)).ljust(10, "-")
            print(f"  • {c:<32} [{bar}] {done}/{total} tasks ({pct:.0f}%)")

    archived_changes = []
    if os.path.exists(ARCHIVE_DIR):
        archived_changes = [
            d for d in os.listdir(ARCHIVE_DIR)
            if os.path.isdir(os.path.join(ARCHIVE_DIR, d)) and not d.startswith(".")
        ]

    print(f"\n[ARCHIVED CHANGES] (Total: {len(archived_changes)})")
    for a in sorted(archived_changes)[-10:]:
        print(f"  ✓ {a}")
    if len(archived_changes) > 10:
        print(f"    ... and {len(archived_changes) - 10} earlier archived changes.")
    print("================================================================================")

def cmd_status(args):
    change_name = args.name.strip().lower().replace(" ", "-")
    target_path = os.path.join(CHANGES_DIR, change_name)

    if not os.path.exists(target_path):
        # Check archive
        archived_matches = [
            d for d in os.listdir(ARCHIVE_DIR)
            if d.endswith(change_name) or d == change_name
        ] if os.path.exists(ARCHIVE_DIR) else []

        if archived_matches:
            target_path = os.path.join(ARCHIVE_DIR, archived_matches[-1])
            print(f"Note: Change '{change_name}' is ARCHIVED at {target_path}")
        else:
            print(f"Error: Change '{change_name}' not found in active or archived directory.")
            sys.exit(1)

    tasks_file = os.path.join(target_path, "tasks.md")
    done, total, items = parse_tasks(tasks_file)
    update_tasks_count(tasks_file, done, total)

    pct = (done / total * 100) if total > 0 else 0
    print(f"\n--- OpenSpec Status: {change_name} ---")
    print(f"Progress: {done}/{total} tasks completed ({pct:.1f}%)\n")

    for is_done, text in items:
        status_mark = "[x]" if is_done else "[ ]"
        print(f"  {status_mark} {text}")

    if done == total and total > 0:
        print("\n✓ All tasks completed! You can archive this change using:")
        print(f"  python openspec_tool.py archive {change_name}")
    else:
        remaining = total - done
        print(f"\n⚡ {remaining} task(s) remaining. Execute with '/opsx-apply'.")

def cmd_archive(args):
    ensure_dirs()
    change_name = args.name.strip().lower().replace(" ", "-")
    target_path = os.path.join(CHANGES_DIR, change_name)

    if not os.path.exists(target_path):
        print(f"Error: Active change '{change_name}' does not exist at {target_path}")
        sys.exit(1)

    tasks_file = os.path.join(target_path, "tasks.md")
    done, total, _ = parse_tasks(tasks_file)

    if done < total and not args.force:
        print(f"Warning: Only {done}/{total} tasks are marked as completed [x] in tasks.md.")
        print("Refusing to archive incomplete change without --force flag.")
        sys.exit(1)

    today = datetime.now().strftime("%Y-%m-%d")
    archive_name = f"{today}-{change_name}"
    archive_path = os.path.join(ARCHIVE_DIR, archive_name)

    # Move directory
    import shutil
    shutil.move(target_path, archive_path)

    print(f"✓ Successfully archived '{change_name}' -> '{archive_path}'")
    print("  Active context cleaned. Token window protected from obsolete specifications.")

def cmd_write_back(args):
    change_name = args.name.strip().lower().replace(" ", "-")
    target_path = os.path.join(CHANGES_DIR, change_name)

    if not os.path.exists(target_path):
        print(f"Error: Active change '{change_name}' not found.")
        sys.exit(1)

    design_file = os.path.join(target_path, "design.md")
    if not os.path.exists(design_file):
        print(f"Error: design.md not found in {target_path}")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    decision_entry = f"\n- **[{timestamp}] Decision Written Back:** {args.decision}\n"

    with open(design_file, "a", encoding="utf-8") as f:
        f.write(decision_entry)

    print(f"✓ Decision successfully written back to {design_file}:")
    print(f"  \"{args.decision}\"")
    print("  Spec drift prevented.")

def cmd_check_boundaries(args):
    """
    Audits git modified files to verify they do not leak outside the designated target folder.
    """
    folder = args.folder.replace("\\", "/").strip("/")
    try:
        res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
    except Exception as e:
        print(f"Error running git status: {e}")
        sys.exit(1)

    lines = res.stdout.strip().splitlines()
    violations = []
    allowed_prefixes = (folder, "openspec/", ".openspec")

    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            file_path = parts[-1].replace("\\", "/")
            if not any(file_path.startswith(prefix) for prefix in allowed_prefixes):
                violations.append(file_path)

    if violations:
        print("================================================================================")
        print("                 [WARNING] SCOPE BOUNDARY VIOLATION DETECTED                    ")
        print("================================================================================")
        print(f"The following modified files leak outside designated folder '{folder}':")
        for v in violations:
            print(f"  ❌ {v}")
        print("\nINVARIANT: 'Agents stay in their folder'. Revert or authorize multi-folder blast radius.")
        sys.exit(1)
    else:
        print(f"✓ Scope boundary verified: All active modifications are strictly confined to '{folder}'.")

def main():
    parser = argparse.ArgumentParser(description="OpenSpec CLI Tool (BRILiaN Way SDD V2)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # new
    p_new = subparsers.add_parser("new", help="Create a new OpenSpec change specification")
    p_new.add_argument("name", help="Name of the change (e.g. growth-mindset-failure-can-continue)")
    p_new.add_argument("--why", help="Explanation of why this change is necessary")
    p_new.add_argument("--what", help="Summary of what changes")
    p_new.add_argument("--folder", help="Target module directory (e.g. src/games/growth)")
    p_new.set_defaults(func=cmd_new)

    # list
    p_list = subparsers.add_parser("list", help="List active and archived OpenSpec changes")
    p_list.set_defaults(func=cmd_list)

    # status
    p_status = subparsers.add_parser("status", help="Inspect tasks progress for a change")
    p_status.add_argument("name", help="Name of the change")
    p_status.set_defaults(func=cmd_status)

    # archive
    p_archive = subparsers.add_parser("archive", help="Archive a completed OpenSpec change")
    p_archive.add_argument("name", help="Name of the change")
    p_archive.add_argument("--force", action="store_true", help="Force archive even if tasks are incomplete")
    p_archive.set_defaults(func=cmd_archive)

    # write-back
    p_wb = subparsers.add_parser("write-back", help="Write runtime implementation decisions back to spec")
    p_wb.add_argument("name", help="Name of the change")
    p_wb.add_argument("--decision", required=True, help="Decision description to record in design.md")
    p_wb.set_defaults(func=cmd_write_back)

    # check-boundaries
    p_cb = subparsers.add_parser("check-boundaries", help="Verify git modified files stay inside target folder")
    p_cb.add_argument("folder", help="Target allowed folder prefix (e.g. src/games/integrity)")
    p_cb.set_defaults(func=cmd_check_boundaries)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
