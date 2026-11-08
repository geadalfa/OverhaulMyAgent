#!/usr/bin/env python3
"""
RTK (Token Killer) CLI Tool - Compact Command Output & Token Compression Utility
Inspired by the Rust Token Killer protocol and BRILiaN Way Arcade sharing session.
Slashes LLM token consumption by 60%-98% across directory listings, command errors,
git logs, file signatures, and AST graph queries.
"""

import sys
import os
import io
import json
import subprocess
import re
import argparse

# Ensure utf-8 output on Windows consoles
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

IGNORED_DIRS = {
    "node_modules", ".git", ".svn", ".hg", "dist", "build", "dist-server",
    "__pycache__", ".pytest_cache", ".venv", "venv", ".idea", ".vscode",
    ".next", ".nuxt", "coverage", ".turbo", "target", "bin", "obj"
}

def format_size(num_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f}{unit}" if unit != 'B' else f"{num_bytes}{unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f}TB"

def cmd_ls(target_path=".", max_depth=2):
    """
    Compact directory listing: groups files and summarizes subdirectories,
    filtering out massive noise folders like node_modules (saving ~98% tokens).
    """
    target_path = os.path.abspath(target_path)
    if not os.path.exists(target_path):
        print(f"Error: Path '{target_path}' does not exist.")
        sys.exit(1)

    print(f"Directory: {target_path}")
    
    entries = []
    try:
        with os.scandir(target_path) as it:
            for entry in it:
                if entry.name in IGNORED_DIRS or entry.name.startswith(".export_stage"):
                    continue
                entries.append(entry)
    except PermissionError as e:
        print(f"Permission denied: {e}")
        return

    # Sort directories first, then files
    dirs = sorted([e for e in entries if e.is_dir()], key=lambda x: x.name.lower())
    files = sorted([e for e in entries if e.is_file()], key=lambda x: x.name.lower())

    for d in dirs:
        # Count items inside
        try:
            sub_count = sum(1 for sub in os.scandir(d.path) if sub.name not in IGNORED_DIRS)
            print(f"  [DIR]  {d.name}/ ({sub_count} items)")
        except Exception:
            print(f"  [DIR]  {d.name}/")

    for f in files:
        try:
            size_str = format_size(f.stat().st_size)
            print(f"  [FILE] {f.name} ({size_str})")
        except Exception:
            print(f"  [FILE] {f.name}")

def cmd_err(command_str):
    """
    Executes an arbitrary shell command and extracts ONLY failure/error lines
    and stack traces, suppressing thousands of lines of passing noise.
    """
    print(f"[*] Executing command: {command_str}")
    proc = subprocess.Popen(
        command_str,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    stdout, stderr = proc.communicate()

    output_lines = []
    if stdout:
        output_lines.extend(stdout.splitlines())
    if stderr:
        output_lines.extend(stderr.splitlines())

    # Look for error indicators
    error_patterns = [
        re.compile(r"error", re.IGNORECASE),
        re.compile(r"failed", re.IGNORECASE),
        re.compile(r"fatal", re.IGNORECASE),
        re.compile(r"exception", re.IGNORECASE),
        re.compile(r"traceback", re.IGNORECASE),
        re.compile(r"panic", re.IGNORECASE),
        re.compile(r"syntaxerror", re.IGNORECASE),
        re.compile(r"referenceerror", re.IGNORECASE),
        re.compile(r"typeerror", re.IGNORECASE),
        re.compile(r"\bFAIL\b"),
        re.compile(r"^\s*at\s+.*\(.*:\d+:\d+\)"),  # Node stack trace
        re.compile(r'^\s*File ".*", line \d+'),    # Python stack trace
    ]

    filtered_lines = []
    capture_context = 0

    for line in output_lines:
        is_err = any(p.search(line) for p in error_patterns)
        if is_err:
            filtered_lines.append(line)
            capture_context = 3  # Capture next 3 lines of stack trace
        elif capture_context > 0:
            filtered_lines.append(line)
            capture_context -= 1

    print(f"[*] Exit Code: {proc.returncode}")
    if proc.returncode == 0 and not filtered_lines:
        print("[✓] Command completed successfully with 0 errors.")
    elif filtered_lines:
        print(f"[*] Filtered Error Lines ({len(filtered_lines)} lines extracted):")
        for line in filtered_lines[:100]:
            print(f"  {line}")
        if len(filtered_lines) > 100:
            print(f"  ... [truncated {len(filtered_lines) - 100} additional error lines]")
    else:
        print(f"[!] Command exited with non-zero code {proc.returncode}, but no specific error patterns matched.")
        for line in output_lines[-20:]:
            print(f"  {line}")

def cmd_read_signatures(file_path):
    """
    Reads a source file and extracts signatures/exports/classes/types without dumping implementation bodies.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    ext = os.path.splitext(file_path)[1].lower()
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    sig_patterns = [
        re.compile(r"^\s*(export\s+)?(default\s+)?(class|interface|type|enum|function|const\s+[A-Za-z0-9_]+\s*=\s*(async\s*)?\()"),
        re.compile(r"^\s*(def|class)\s+[A-Za-z0-9_]+"),
        re.compile(r"^\s*(pub\s+)?(fn|struct|enum|trait|type|impl)\s+"),
        re.compile(r"^\s*(func|type|interface)\s+"),
    ]

    print(f"Signatures for {file_path} ({len(lines)} total lines):")
    found = 0
    for idx, line in enumerate(lines, 1):
        if any(p.search(line) for p in sig_patterns):
            print(f"  L{idx:4d}: {line.strip()}")
            found += 1

    if found == 0:
        print(f"  No top-level signatures detected. Showing first 30 lines:")
        for idx, line in enumerate(lines[:30], 1):
            print(f"  L{idx:4d}: {line.rstrip()}")

def cmd_json_skeleton(file_path):
    """
    Emits JSON structure without massive value arrays or objects.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    def skeleton(obj):
        if isinstance(obj, dict):
            return {k: skeleton(v) for k, v in list(obj.items())[:10]}
        elif isinstance(obj, list):
            if len(obj) == 0:
                return []
            return [f"Array[{len(obj)} items of type {type(obj[0]).__name__}]", skeleton(obj[0])]
        else:
            return type(obj).__name__

    print(json.dumps(skeleton(data), indent=2))

def cmd_query_graph(node_name, graph_path="graphify-out/graph.json"):
    """
    Queries an AST Knowledge Graph (Graphify) for a specific node,
    fetching edges and neighbors in 500 tokens instead of reading 200K tokens.
    """
    if not os.path.exists(graph_path):
        # Check scratch or parents
        candidates = [
            graph_path,
            os.path.join(".", "graphify-out", "graph.json"),
            os.path.join("..", "graphify-out", "graph.json"),
            r"~/.gemini/antigravity\scratch\bw-games\graphify-out\graph.json"
        ]
        found = None
        for c in candidates:
            if os.path.exists(c):
                found = c
                break
        if not found:
            print(f"Error: Knowledge graph not found at {graph_path}.")
            sys.exit(1)
        graph_path = found

    print(f"[*] Querying graph at {graph_path} for node: '{node_name}'...")
    with open(graph_path, "r", encoding="utf-8") as f:
        graph = json.load(f)

    nodes = graph.get("nodes", [])
    edges = graph.get("links", []) or graph.get("edges", [])

    matched_nodes = [n for n in nodes if node_name.lower() in str(n.get("id", "")).lower() or node_name.lower() in str(n.get("name", "")).lower()]

    if not matched_nodes:
        print(f"[-] No nodes matching '{node_name}' found in graph.")
        return

    print(f"[+] Found {len(matched_nodes)} matching node(s):")
    for n in matched_nodes[:5]:
        nid = n.get("id")
        nname = n.get("name", nid)
        ncomm = n.get("community", "N/A")
        print(f"\n--- Node: {nname} (ID: {nid}, Community: {ncomm}) ---")
        
        # Find incoming & outgoing edges
        incoming = []
        outgoing = []
        for e in edges:
            src = e.get("source") if isinstance(e.get("source"), str) else e.get("source", {}).get("id")
            tgt = e.get("target") if isinstance(e.get("target"), str) else e.get("target", {}).get("id")
            rel = e.get("type") or e.get("relationship") or "connects"
            
            if src == nid:
                outgoing.append(f"--[{rel}]--> {tgt}")
            elif tgt == nid:
                incoming.append(f"<--[{rel}]-- {src}")

        print(f"  Connections ({len(incoming) + len(outgoing)}):")
        for inc in incoming[:10]:
            print(f"    {inc}")
        for out in outgoing[:10]:
            print(f"    {out}")
        if len(incoming) + len(outgoing) > 20:
            print(f"    ... [truncated {len(incoming) + len(outgoing) - 20} additional edges]")

def main():
    parser = argparse.ArgumentParser(description="RTK Token Compression & Output Filter CLI")
    subparsers = parser.add_subparsers(dest="command")

    # ls
    ls_parser = subparsers.add_parser("ls", help="Compact directory listing")
    ls_parser.add_argument("path", nargs="?", default=".", help="Directory to list")

    # err
    err_parser = subparsers.add_parser("err", help="Run command and extract only error lines")
    err_parser.add_argument("cmd", help="Command to execute")

    # read
    read_parser = subparsers.add_parser("read", help="Extract code signatures and interface definitions")
    read_parser.add_argument("file", help="File to inspect")

    # json
    json_parser = subparsers.add_parser("json", help="Inspect JSON schema skeleton without values")
    json_parser.add_argument("file", help="JSON file to inspect")

    # graph
    graph_parser = subparsers.add_parser("graph", help="Query Graphify AST knowledge graph for symbol")
    graph_parser.add_argument("node", help="Symbol or node name to search")
    graph_parser.add_argument("--graph", default="graphify-out/graph.json", help="Path to graph.json")

    args = parser.parse_args()

    if args.command == "ls":
        cmd_ls(args.path)
    elif args.command == "err":
        cmd_err(args.cmd)
    elif args.command == "read":
        cmd_read_signatures(args.file)
    elif args.command == "json":
        cmd_json_skeleton(args.file)
    elif args.command == "graph":
        cmd_query_graph(args.node, args.graph)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
