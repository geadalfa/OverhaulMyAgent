#!/usr/bin/env python3
"""
fetch_web.py
Zero-Lag Web Content Extraction Tool for macOS & Windows.
Automatically detects static vs JavaScript-heavy pages (Gemini Share, Notion, SPAs).
Strips noise and outputs clean, dense Markdown without token waste.
"""

import argparse
import html
import os
import re
import subprocess
import sys
import urllib.request

def find_headless_browser():
    # macOS paths
    candidates = [
        "/Applications/Opera.app/Contents/MacOS/Opera",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    ]
    # Windows paths
    candidates.extend([
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    ])
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def fetch_with_browser(url, browser_bin, wait_ms=10000):
    cmd = [
        browser_bin,
        "--headless",
        f"--virtual-time-budget={wait_ms}",
        "--dump-dom",
        url
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25, check=True)
        return res.stdout.decode("utf-8", errors="ignore")
    except Exception as e:
        sys.stderr.write(f"Browser headless fetch error: {e}\n")
        return None

def fetch_static(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        sys.stderr.write(f"Static fetch error: {e}\n")
        return None

def html_to_clean_markdown(raw_html, url=""):
    # Strip scripts, styles, svg, iframes, nav, header, footer
    clean = re.sub(r'<script[^>]*>.*?</script>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<svg[^>]*>.*?</svg>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<header[^>]*>.*?</header>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<footer[^>]*>.*?</footer>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<nav[^>]*>.*?</nav>', '', clean, flags=re.DOTALL | re.IGNORECASE)

    # Special handling for Gemini share pages
    if "gemini.google.com" in url or "share.gemini.google" in url:
        queries = re.findall(r'<user-query[^>]*>(.*?)</user-query>', clean, flags=re.DOTALL | re.IGNORECASE)
        responses = re.findall(r'<message-content[^>]*>(.*?)</message-content>', clean, flags=re.DOTALL | re.IGNORECASE)
        if queries or responses:
            out = []
            turns = max(len(queries), len(responses))
            for i in range(turns):
                out.append(f"## Turn {i+1}\n")
                if i < len(queries):
                    q_text = re.sub(r'<[^>]+>', ' ', queries[i])
                    q_text = html.unescape(q_text)
                    q_text = re.sub(r'\s+', ' ', q_text).strip()
                    if q_text.startswith("You said"):
                        q_text = q_text[8:].strip()
                    out.append(f"### User\n{q_text}\n")
                if i < len(responses):
                    r_text = responses[i]
                    r_text = re.sub(r'<pre[^>]*><code[^>]*>', '\n```\n', r_text)
                    r_text = re.sub(r'</code></pre>', '\n```\n', r_text)
                    r_text = re.sub(r'<p[^>]*>', '\n\n', r_text)
                    r_text = re.sub(r'<li[^>]*>', '\n- ', r_text)
                    r_text = re.sub(r'<br\s*/?>', '\n', r_text)
                    r_text = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'\n### \1\n', r_text)
                    r_text = re.sub(r'<[^>]+>', '', r_text)
                    r_text = html.unescape(r_text)
                    out.append(f"### Assistant\n{r_text.strip()}\n")
            return "\n".join(out)

    # General HTML conversion
    clean = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\n# \1\n', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n## \1\n', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n### \1\n', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<pre[^>]*><code[^>]*>', '\n```\n', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'</code></pre>', '\n```\n', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<p[^>]*>', '\n\n', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<li[^>]*>', '\n- ', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<br\s*/?>', '\n', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<[^>]+>', '', clean)
    clean = html.unescape(clean)
    clean = re.sub(r'\n{3,}', '\n\n', clean)
    return clean.strip()

def main():
    parser = argparse.ArgumentParser(description="Fetch and extract dense Markdown from any web URL")
    parser.add_argument("url", help="Web page URL to fetch")
    parser.add_argument("--out", help="Save output to file path")
    parser.add_argument("--max-chars", type=int, default=12000, help="Maximum characters to print to stdout")

    args = parser.parse_args()

    # Determine if URL is SPA (Gemini, Claude, Notion, etc.)
    is_spa = any(k in args.url for k in ["gemini.google.com", "share.gemini.google", "claude.ai", "notion.site", "chatgpt.com"])

    browser_bin = find_headless_browser()
    raw_html = None

    if is_spa and browser_bin:
        raw_html = fetch_with_browser(args.url, browser_bin)
    
    if not raw_html:
        raw_html = fetch_static(args.url)
        if not raw_html and browser_bin:
            raw_html = fetch_with_browser(args.url, browser_bin)

    if not raw_html:
        sys.stderr.write("Failed to fetch web content.\n")
        sys.exit(1)

    md = html_to_clean_markdown(raw_html, args.url)

    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Content saved to: {args.out} ({len(md)} chars)")
    else:
        if len(md) > args.max_chars:
            print(md[:args.max_chars] + f"\n\n... [Truncated: {len(md) - args.max_chars} more characters. Use --out to save full content.]")
        else:
            print(md)

if __name__ == "__main__":
    main()
