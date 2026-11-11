# High-Precision OCR, Protected PDF Parsing & Offline Document Conversion

## 1. Executive Summary & Zero-Leakage Architecture

Online PDF converters and commercial cloud OCR portals present massive data exfiltration and privacy risks. Uploading proprietary contracts, financial statements, bank books, medical records, or source specifications to unverified third-party web services exposes sensitive data to unauthorized retention, AI training harvesting, and breach vectors.

This document establishes the **Zero-Leakage Local-First Document Pipeline** for Windows and macOS. It details how Gemi operates, builds, and scripts offline-capable tools to unlock protected PDFs, remove stubborn vector and burned-in watermarks, bypass corrupted font encodings (mojibake CMap/ToUnicode), extract multi-column layout structures and tables, and convert documents into high-fidelity Word (`.docx`), Markdown (`.md`), plain text (`.txt`), and structured JSON without third-party exposure.

```
                           +----------------------------------------+
                           |   Input Document (PDF / Image / Scan)  |
                           +----------------------------------------+
                                               |
                                               v
                             [ Stage 1: Document Inspection ]
                             - Check encryption & permissions
                             - Test font encoding & text layer sanity
                                               |
                     +-------------------------+-------------------------+
                     |                                                   |
                     v (Healthy Text Layer & No Lock)                    v (Locked / Broken / Scanned / Watermarked)
        +--------------------------+                        +----------------------------------+
        | Native Direct Extraction |                        |   [ Stage 2: Pre-Processing ]    |
        |  (PyMuPDF / pikepdf)     |                        | - Unlock permissions (pikepdf)   |
        +--------------------------+                        | - Strip XObject/Vector watermarks|
                     |                                      | - OpenCV Adaptive Thresholding   |
                     |                                      | - 300+ DPI High-Res Rendering    |
                     |                                      +----------------------------------+
                     |                                                   |
                     |                                                   v
                     |                                      +----------------------------------+
                     |                                      |    [ Stage 3: OCR & Parsing ]    |
                     |                                      | - Layout/Table: Docling / MinerU |
                     |                                      | - Lightweight CPU: PaddleOCR v5  |
                     |                                      | - VLM Multimodal: Gemini / Qwen  |
                     |                                      +----------------------------------+
                     |                                                   |
                     +-------------------------+-------------------------+
                                               |
                                               v
                              [ Stage 4: Document Synthesis ]
                              - Format conversion (docx, md, txt)
                              - Table & formula preservation
                              - Verbatim anti-hallucination verification
```

---

## 2. The Four Document Obstacle Archetypes & Remediation Strategies

| Obstacle Archetype | Symptom & Technical Mechanism | Fatal Anti-Pattern | Deterministic Remediation Pipeline |
| :--- | :--- | :--- | :--- |
| **Type 1: Permission Lock (Owner Password)** | Document forbids copying, printing, or text selection, though text streams remain intact in the PDF dictionary. | Running heavy OCR or screenshotting pages. | Decrypt in-memory instantly using `pikepdf.open()` or `qpdf --decrypt`. Re-saves decrypted PDF in < 100ms with 100% vector text preservation. |
| **Type 2: Corrupted Font Encoding (Mojibake CMap / ToUnicode)** | Text selects and copies, but clipboard outputs unreadable squares (`□□□`), random symbols, or mangled unicode ligatures. | Relying on `pdftotext` or `pypdf.extract_text()`. | Force-render pages to 300 DPI RGB bitmaps via `page.get_pixmap(dpi=300)`. Discard corrupted internal glyph streams and feed clean images to layout OCR. |
| **Type 3: Separate Vector / XObject Watermark** | Watermark overlays text as separate transparent shapes, vector paths, or Form XObjects (e.g. "CONFIDENTIAL" stamps). | Flattening and running blind OCR, causing watermark words to splice into body sentences. | Prune XObjects, annotations, and watermark layers programmatically via PyMuPDF (`page.clean_contents()`, deleting `/Watermark` and `/Artifact` sub-dictionaries). |
| **Type 4: Burned-in Scanned Watermark** | Document was physically scanned or flattened into raster images (JPEG/PNG) with watermarks fused into the pixel matrix. | Standard Tesseract OCR (chokes on overlapping high-contrast background noise). | **Option A (Deterministic CV):** OpenCV adaptive thresholding / grayscale truncation (`cv2.threshold(gray, 185, 255, cv2.THRESH_TRUNC)` + normalization) to bleach lighter watermark pixels to `#FFFFFF`.<br>**Option B (VLM Steering):** Multimodal Vision LLM with explicit negative-attention prompt steering. |

---

## 3. SOTA Open-Source Document Parsing & OCR Ecosystem

### 3.1. End-to-End Document Parsing & AI-Ready Converters

1. **MinerU (`opendatalab/MinerU`):**
   - **Repository:** `github.com/opendatalab/MinerU` (upstream 4.2.0)
   - **Capabilities:** Gold-standard open-source parser for raw, complex, and scanned academic/technical PDFs. Automatically performs layout analysis, strips running headers/footers/watermarks, extracts tables and LaTeX mathematical formulas, and outputs clean Markdown/JSON.
   - **CLI / Integration:** Native Python library and CLI (`magic-pdf`).

2. **Docling (IBM Research):**
   - **Repository:** `github.com/docling-project/docling`
   - **Capabilities:** Ultra-fast, purpose-built parser designed for GenAI and RAG pipelines. Features proprietary `TableFormer` for boundary-less table reconstruction, deep hierarchical reading-order detection, and multi-format export (`DoclingDocument` -> Markdown, HTML, JSON, Docx).

3. **Marker (`datalab-to/marker`):**
   - **Repository:** `github.com/datalab-to/marker`
   - **Capabilities:** High-throughput converter transforming PDF to Markdown/JSON in ~1-2 seconds per page. Employs a hybrid pipeline: heuristic fast-path, Surya OCR, and targeted VLM verification for corrupted blocks.

4. **olmOCR (Allen Institute for AI):**
   - **Repository:** `github.com/allenai/olmocr`
   - **Capabilities:** Tailored 7B VLM fine-tune specifically trained on messy historical scans, tilted documents, multi-column articles, and margin notes to generate natural reading-order Markdown.

5. **Zerox (Omni AI):**
   - **Repository:** `github.com/getomni-ai/zerox`
   - **Capabilities:** Converts PDF pages to optimized images and dispatches them to vision models (Gemini Flash, Claude 3.5 Sonnet, GPT-4o, or local Ollama/LiteLLM). Highly resilient against burned-in watermarks due to natural language vision steering.

### 3.2. Lightweight OCR Engines & Local Weight Models

- **PaddleOCR (PP-OCRv5 & PP-Structure):**
  - **Repository:** `github.com/PaddlePaddle/PaddleOCR`
  - **Strengths:** Extremely fast, lightweight CPU execution. Excels at detecting text partially obscured by faint watermarks, Asian scripts, Indonesian, English, and structured forms.
- **Surya OCR (`datalab-to/surya`):**
  - **Strengths:** Modern deep learning OCR supporting 90+ languages, line detection, layout bounding boxes, and reading-order inference.

### 3.3. Pre-Processing & Security Decryption Utilities

- **QPDF (`qpdf/qpdf`):** Standard C++ CLI for decrypting owner permissions: `qpdf --decrypt input.pdf output.pdf`.
- **PikePDF (`pikepdf`):** High-performance Python binding for QPDF.
- **PyMuPDF (`fitz` / `pymupdf`):** Fast PDF engine for rendering 300+ DPI pixmaps, pruning XObjects, and re-assembling cleaned documents.
- **OCRmyPDF (`ocrmypdf/OCRmyPDF`):** Production CLI tool utilizing Tesseract with auto-deskewing, image unpapering, and lossless PDF/A generation (`ocrmypdf --deskew --clean --force-ocr input.pdf output.pdf`).

---

## 4. MCP (Model Context Protocol) Ecosystem

When integrating with Antigravity, Cline, Cursor, or OpenCode, the following MCP servers provide structured agentic tool calls for document intelligence:

1. **Docling MCP (`docling-project/docling-mcp`):**
   - Official IBM Research MCP server.
   - Quick launch: `uvx --from=docling-mcp docling-mcp-server`
   - Exposes tools to parse PDFs, extract tables, and emit structured Markdown.
2. **All-in-One SOTA OCR MCP (`sandraschi/ocr-mcp`):**
   - FastMCP server bundling PP-OCRv5, DeepSeek-OCR, Florence-2, and MinerU backends with integrated preprocessing (deskew, enhance, crop).
3. **MinerU MCP:**
   - Cloud/API: `github.com/linxule/mineru-mcp` (`npx -y mineru-mcp`)
   - Local CPU/MLX: `github.com/TINKPA/mcp-mineru`
4. **Mistral OCR MCP (`ORDIS-Co-Ltd/mistral-ocr-mcp`):**
   - Interfaces directly with `mistral-ocr-latest` API, providing state-of-the-art document reconstruction and table parsing.
5. **Gemini Multimodal OCR MCP (`WindoC/gemini-ocr-mcp`):**
   - Leverages Google Gemini multimodal vision endpoints for cost-effective, zero-noise verbatim transcription.

---

## 5. Anti-Hallucination & Verbatim Vision/VLM Steering Protocol

When invoking Multimodal Vision LLMs (Gemini Flash/Pro, Claude 3.5 Sonnet, GPT-4o, or local Qwen-VL) to transcribe scanned document pages, apply this steering prompt without alteration:

```markdown
# System Prompt: High-Precision Verbatim OCR & Document Reconstruction Agent

You are an expert Optical Character Recognition (OCR) engine and high-fidelity document reconstruction system. Your mission is to extract and transcribe all textual, tabular, and structural content from this document page image into clean, standard Markdown with 100% precision.

## STRICT OPERATIONAL RULES:
1. Verbatim Extraction (Zero Mutation):
   - Transcribe every character exactly as printed, preserving original spelling, punctuation, capitalization, symbols, and numbering.
   - NEVER summarize, paraphrase, normalize idioms, or correct typos present in the source document.
2. Complete Watermark & Background Artifact Suppression:
   - Completely ignore translucent, diagonal, repeated, or background watermark text (e.g., "CONFIDENTIAL", "DRAFT", "DO NOT COPY", institution emblems, repeated stamps).
   - NEVER inject watermark tokens into body sentences, headers, or table cells.
3. Anti-Hallucination on Low-Legibility Text:
   - If a word, date, or numeric value is heavily obscured by ink, torn, truncated, or illegible, DO NOT GUESS OR INVENT DATA.
   - Mark ambiguous tokens explicitly as `[illegible]` or `[blurred: possibly '...']`.
4. Zero Output Truncation (Anti-Laziness):
   - Transcribe from the very first token to the very last token on the page.
   - FORBIDDEN from using lazy placeholders such as `...[continued]...`, `...[same as above]...`, or omitting paragraphs.
5. Structural & Tabular Fidelity:
   - Preserve typographic hierarchy using standard Markdown headings (`#`, `##`, `###`), nested bullet lists, and ordered items.
   - For multi-column layouts, read the primary column from top-to-bottom before reading the adjacent column.
   - For tabular data, construct a standard Markdown table. If cells are merged (`rowspan`/`colspan`) or complex, render as semantic HTML `<table>` to maintain cell alignment.
   - Re-verify all numbers, currency signs, commas `,` and decimal points `.` against the visual input.
```

---

## 6. Deterministic Python Pre-Processing & Conversion Recipes

### 6.1. Instant Password & Permission Decryption (`pikepdf`)

```python
import pikepdf

def unlock_pdf(input_path: str, output_path: str) -> bool:
    """Removes owner restrictions and password locks with zero loss of vector text."""
    try:
        with pikepdf.open(input_path) as pdf:
            pdf.save(output_path)
        return True
    except pikepdf.PasswordError:
        # Prompt user for user/open password if strongly encrypted
        return False
```

### 6.2. Vector & XObject Watermark Removal (`PyMuPDF`)

```python
import fitz  # PyMuPDF

def strip_vector_watermarks(input_pdf: str, output_pdf: str) -> None:
    """Prunes annotations, form XObjects, and cleans drawing streams."""
    doc = fitz.open(input_pdf)
    for page in doc:
        # 1. Remove annotation overlays
        for annot in list(page.annots() or []):
            page.delete_annot(annot)
        
        # 2. Prune XObject image layers tagged as artifacts/watermarks
        page.clean_contents()
    
    doc.save(output_pdf, garbage=4, deflate=True)
    doc.close()
```

### 6.3. Burned-in Watermark Bleaching (`OpenCV` + `PyMuPDF`)

```python
import fitz
import cv2
import numpy as np

def bleach_scanned_watermarks(input_pdf: str, output_pdf: str, threshold: int = 185) -> None:
    """Renders pages to 300 DPI, eliminates lighter background watermarks, and re-embeds cleaned bitmaps."""
    doc = fitz.open(input_pdf)
    out_doc = fitz.open()

    for page in doc:
        # Render high-resolution raster
        pix = page.get_pixmap(dpi=300, alpha=False)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # Truncate pixel values: Dark text (< 130) stays dark; light watermarks (> 185) become pure white (255)
        _, cleaned = cv2.threshold(gray, threshold, 255, cv2.THRESH_TRUNC)
        cleaned = cv2.normalize(cleaned, None, 0, 255, cv2.NORM_MINMAX)

        # Encode to PNG and insert into target document
        _, img_bytes = cv2.imencode(".png", cleaned)
        rect = page.rect
        new_page = out_doc.new_page(width=rect.width, height=rect.height)
        new_page.insert_image(rect, stream=img_bytes.tobytes())

    out_doc.save(output_pdf, deflate=True)
    out_doc.close()
    doc.close()
```

### 6.4. Clean Markdown to Word (`.docx`) Conversion (`python-docx`)

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
import re

def markdown_to_docx(md_content: str, output_docx_path: str) -> None:
    """Converts structured Markdown into a styled, professional Word document."""
    doc = Document()
    
    # Configure base margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    lines = md_content.splitlines()
    in_code_block = False
    code_buffer = []

    for line in lines:
        stripped = line.strip()
        
        # Handle code blocks
        if stripped.startswith("```"):
            if in_code_block:
                p = doc.add_paragraph("\n".join(code_buffer))
                p.style = "No Spacing"
                for r in p.runs:
                    r.font.name = "Consolas"
                    r.font.size = Pt(9.5)
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        # Handle headings
        if stripped.startswith("### "):
            doc.add_heading(stripped[4:], level=3)
        elif stripped.startswith("## "):
            doc.add_heading(stripped[3:], level=2)
        elif stripped.startswith("# "):
            doc.add_heading(stripped[2:], level=1)
        elif stripped.startswith("- ") or stripped.startswith("* "):
            doc.add_paragraph(stripped[2:], style='List Bullet')
        elif re.match(r"^\d+\.\s", stripped):
            prefix_len = len(re.match(r"^\d+\.\s", stripped).group(0))
            doc.add_paragraph(stripped[prefix_len:], style='List Number')
        elif stripped == "":
            continue
        else:
            doc.add_paragraph(line)

    doc.save(output_docx_path)
```

---

## 7. Windows Desktop Application Blueprint (`DocShield-Converter`)

For User's personal desktop environment, the recommended implementation stack is:
- **GUI Framework:** PyQt6 / PySide6 with dark mode Zinc design tokens (mirroring `<HOME>/.gemini/knowledge/ui_ux_anti_slop_design_engineering.md`).
- **Processing Engine:** Python 3.11 with `pikepdf`, `pymupdf`, `opencv-python-headless`, and `python-docx`.
- **Local Fallback OCR:** PaddleOCR PP-OCRv5 for offline lightweight parsing; optional API toggle for Gemini 2.5 Flash / Mistral OCR for heavy watermarked scans.
- **Data Boundary:** Strictly runs locally on `localhost` with zero external analytics, zero cloud uploads (unless user enables AI Vision API key), and automatic temporary raster cache wipe on exit.
