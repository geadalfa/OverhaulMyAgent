#!/usr/bin/env python3
"""
Microsoft LLMLingua / LongLLMLingua Token Compressor Utility
Author: Gemi for User
Usage:
    python compress_prompt.py --file path/to/document.txt --rate 0.5
    python compress_prompt.py --text "long prompt text..." --rate 0.4
"""

import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Compress prompts using Microsoft LLMLingua")
    parser.add_argument("--file", "-f", help="Path to input text file to compress")
    parser.add_argument("--text", "-t", help="Raw text string to compress")
    parser.add_argument("--rate", "-r", type=float, default=0.5, help="Target compression rate (0.1 to 0.9, default 0.5)")
    parser.add_argument("--output", "-o", help="Optional output file path to write compressed text")
    args = parser.parse_args()

    content = ""
    if args.file:
        if not os.path.exists(args.file):
            print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    elif args.text:
        content = args.text
    else:
        parser.print_help()
        sys.exit(1)

    print(f"[INFO] Initial text length: {len(content)} characters (~{len(content)//4} tokens)")
    print(f"[INFO] Initializing Microsoft LLMLingua compressor (rate: {args.rate})...")

    try:
        from llmlingua import PromptCompressor
        compressor = PromptCompressor(
            model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
            use_llmlingua2=True
        )
        result = compressor.compress_prompt(
            content,
            rate=args.rate,
            use_bpe=True
        )
        compressed_text = result.get("compressed_prompt", "")
        origin_tokens = result.get("origin_tokens", len(content)//4)
        compressed_tokens = result.get("compressed_tokens", len(compressed_text)//4)
        ratio = result.get("ratio", f"{(compressed_tokens / max(origin_tokens, 1)):.2f}x")

        print(f"[SUCCESS] Compression complete!")
        print(f"   Original tokens  : {origin_tokens}")
        print(f"   Compressed tokens: {compressed_tokens} ({ratio} compression ratio)")
        print(f"   Tokens saved     : {origin_tokens - compressed_tokens} tokens")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as out_f:
                out_f.write(compressed_text)
            print(f"[INFO] Saved compressed prompt to: {args.output}")
        else:
            print("\n--- COMPRESSED PROMPT PREVIEW ---")
            print(compressed_text[:500] + ("..." if len(compressed_text) > 500 else ""))

    except Exception as e:
        print(f"[ERROR] LLMLingua compression failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
