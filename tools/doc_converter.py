#!/usr/bin/env python3
"""
doc_converter.py
Zero-Leakage Local-First Document Processor & Format Converter for User.
Handles permission unlocking, watermark bleaching, high-res rasterization,
and synthesis into Word (.docx), Markdown (.md), and plain text (.txt).
"""

import argparse
import os
import re
import sys

def unlock_pdf(input_path: str, output_path: str) -> bool:
    try:
        import pikepdf
        with pikepdf.open(input_path) as pdf:
            pdf.save(output_path)
        print(f"[OK] Unlocked permissions and saved to: {output_path}")
        return True
    except ImportError:
        print("[ERR] pikepdf is not installed.")
        return False
    except Exception as e:
        print(f"[ERR] Failed to unlock {input_path}: {e}")
        return False

def clean_watermarks(input_path: str, output_path: str, threshold: int = 185, dpi: int = 300) -> bool:
    try:
        import fitz  # PyMuPDF
        import cv2
        import numpy as np

        doc = fitz.open(input_path)
        out_doc = fitz.open()

        print(f"[*] Processing {len(doc)} pages with OpenCV thresholding ({threshold})...")
        for i, page in enumerate(doc):
            # 1. Clean annotations and vector artifacts
            for annot in list(page.annots() or []):
                page.delete_annot(annot)
            page.clean_contents()

            # 2. Render to high-res bitmap
            pix = page.get_pixmap(dpi=dpi, alpha=False)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)

            # 3. Grayscale and threshold bleaching
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            _, cleaned = cv2.threshold(gray, threshold, 255, cv2.THRESH_TRUNC)
            cleaned = cv2.normalize(cleaned, None, 0, 255, cv2.NORM_MINMAX)

            # 4. Re-embed into output PDF
            _, img_bytes = cv2.imencode(".png", cleaned)
            rect = page.rect
            new_page = out_doc.new_page(width=rect.width, height=rect.height)
            new_page.insert_image(rect, stream=img_bytes.tobytes())

        out_doc.save(output_path, deflate=True)
        out_doc.close()
        doc.close()
        print(f"[OK] Bleached watermarked PDF saved to: {output_path}")
        return True
    except ImportError as e:
        print(f"[ERR] Missing dependency for watermark cleaning: {e}")
        return False
    except Exception as e:
        print(f"[ERR] Watermark cleaning failed: {e}")
        return False

def render_pages_to_images(input_path: str, output_dir: str, dpi: int = 300) -> list:
    os.makedirs(output_dir, exist_ok=True)
    images = []
    try:
        import fitz
        doc = fitz.open(input_path)
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=dpi, alpha=False)
            out_img = os.path.join(output_dir, f"page_{i+1:03d}.png")
            pix.save(out_img)
            images.append(out_img)
        doc.close()
        print(f"[OK] Rendered {len(images)} pages at {dpi} DPI to {output_dir}")
        return images
    except Exception as e:
        print(f"[ERR] Failed rendering pages: {e}")
        return []

def pdf_to_markdown(input_path: str, output_md_path: str) -> str:
    try:
        import pymupdf4llm
        md_text = pymupdf4llm.to_markdown(input_path)
        os.makedirs(os.path.dirname(os.path.abspath(output_md_path)), exist_ok=True)
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(md_text)
        print(f"[OK] Markdown extracted ({len(md_text)} chars) -> {output_md_path}")
        return md_text
    except Exception as e:
        print(f"[ERR] Failed to extract Markdown from PDF: {e}")
        return ""

def pdf_to_text(input_path: str, output_txt_path: str) -> str:
    try:
        import pymupdf4llm
        text = pymupdf4llm.to_text(input_path)
        os.makedirs(os.path.dirname(os.path.abspath(output_txt_path)), exist_ok=True)
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[OK] Text extracted ({len(text)} chars) -> {output_txt_path}")
        return text
    except Exception as e:
        print(f"[ERR] Failed to extract text: {e}")
        return ""

def markdown_to_docx(md_path_or_content: str, output_docx_path: str, is_content: bool = False) -> bool:
    try:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor

        if is_content:
            content = md_path_or_content
        else:
            with open(md_path_or_content, "r", encoding="utf-8") as f:
                content = f.read()

        doc = Document()
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        lines = content.splitlines()
        in_code_block = False
        code_buffer = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("```"):
                if in_code_block:
                    p = doc.add_paragraph("\n".join(code_buffer))
                    p.style = "No Spacing"
                    for r in p.runs:
                        r.font.name = "Consolas"
                        r.font.size = Pt(9.5)
                        r.font.color.rgb = RGBColor(0x27, 0x27, 0x2A)
                    code_buffer = []
                    in_code_block = False
                else:
                    in_code_block = True
                continue

            if in_code_block:
                code_buffer.append(line)
                continue

            if stripped.startswith("### "):
                doc.add_heading(stripped[4:], level=3)
            elif stripped.startswith("## "):
                doc.add_heading(stripped[3:], level=2)
            elif stripped.startswith("# "):
                doc.add_heading(stripped[2:], level=1)
            elif stripped.startswith("- ") or stripped.startswith("* "):
                doc.add_paragraph(stripped[2:], style="List Bullet")
            elif re.match(r"^\d+\.\s", stripped):
                prefix_len = len(re.match(r"^\d+\.\s", stripped).group(0))
                doc.add_paragraph(stripped[prefix_len:], style="List Number")
            elif stripped == "":
                continue
            else:
                doc.add_paragraph(line)

        os.makedirs(os.path.dirname(os.path.abspath(output_docx_path)), exist_ok=True)
        doc.save(output_docx_path)
        print(f"[OK] Word document successfully created at: {output_docx_path}")
        return True
    except ImportError:
        print("[ERR] python-docx is not installed.")
        return False
    except Exception as e:
        print(f"[ERR] Failed to generate DOCX: {e}")
        return False

def pdf_to_docx(input_path: str, output_docx_path: str) -> bool:
    try:
        import pymupdf4llm
        print(f"[*] Extracting layout and tables to structured Markdown...")
        md_text = pymupdf4llm.to_markdown(input_path)
        print(f"[*] Synthesizing DOCX from Markdown ({len(md_text)} chars)...")
        return markdown_to_docx(md_text, output_docx_path, is_content=True)
    except Exception as e:
        print(f"[ERR] Failed to convert PDF to DOCX: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Zero-Leakage Local Document Processor & Converter")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Unlock
    unlock_p = subparsers.add_parser("unlock", help="Remove permission locks and passwords from PDF")
    unlock_p.add_argument("input", help="Path to locked input PDF")
    unlock_p.add_argument("output", help="Path to decrypted output PDF")

    # Clean Watermark
    clean_p = subparsers.add_parser("clean-watermark", help="Bleach watermarks using OpenCV thresholding")
    clean_p.add_argument("input", help="Path to input PDF")
    clean_p.add_argument("output", help="Path to cleaned output PDF")
    clean_p.add_argument("--threshold", type=int, default=185, help="Grayscale threshold for bleaching (default 185)")
    clean_p.add_argument("--dpi", type=int, default=300, help="DPI rendering resolution (default 300)")

    # Render Pages
    render_p = subparsers.add_parser("render", help="Render PDF pages to high-res PNG images")
    render_p.add_argument("input", help="Path to input PDF")
    render_p.add_argument("output_dir", help="Directory to save rendered page PNGs")
    render_p.add_argument("--dpi", type=int, default=300, help="DPI resolution (default 300)")

    # PDF to Markdown
    pdf2md_p = subparsers.add_parser("pdf2md", help="Extract PDF directly to clean Markdown with tables")
    pdf2md_p.add_argument("input", help="Path to input PDF")
    pdf2md_p.add_argument("output", help="Path to output Markdown (.md) file")

    # PDF to Text
    pdf2txt_p = subparsers.add_parser("pdf2txt", help="Extract PDF directly to clean plain text")
    pdf2txt_p.add_argument("input", help="Path to input PDF")
    pdf2txt_p.add_argument("output", help="Path to output text (.txt) file")

    # PDF to DOCX
    pdf2docx_p = subparsers.add_parser("pdf2docx", help="Convert PDF directly to styled Word document (.docx)")
    pdf2docx_p.add_argument("input", help="Path to input PDF")
    pdf2docx_p.add_argument("output", help="Path to output Word (.docx) file")

    # MD to DOCX
    md2docx_p = subparsers.add_parser("md2docx", help="Convert Markdown file to Word (.docx)")
    md2docx_p.add_argument("input", help="Path to input Markdown (.md) file")
    md2docx_p.add_argument("output", help="Path to output Word (.docx) file")

    args = parser.parse_args()

    if args.command == "unlock":
        unlock_pdf(args.input, args.output)
    elif args.command == "clean-watermark":
        clean_watermarks(args.input, args.output, threshold=args.threshold, dpi=args.dpi)
    elif args.command == "render":
        render_pages_to_images(args.input, args.output_dir, dpi=args.dpi)
    elif args.command == "pdf2md":
        pdf_to_markdown(args.input, args.output)
    elif args.command == "pdf2txt":
        pdf_to_text(args.input, args.output)
    elif args.command == "pdf2docx":
        pdf_to_docx(args.input, args.output)
    elif args.command == "md2docx":
        markdown_to_docx(args.input, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
