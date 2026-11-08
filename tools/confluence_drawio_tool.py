#!/usr/bin/env python3
"""
confluence_drawio_tool.py
Automates the end-to-end publishing, versioning, and maintenance of Draw.io
Activity Diagrams and Architecture Diagrams on Atlassian Confluence Server.

Features:
- Dual-attachment upload: {diagram_name} (mxfile) + {diagram_name}.png
- Automatic attachment ID discovery & version update (/child/attachment/{id}/data)
- Clean injection of Expand macro + Draw.io macro (Activity & Architecture types)
- Direct macro revision updater (set-revision) to eliminate the "Stuck Revision" trap
- Deep verification of rendered view HTML (body.view) decoding base64 data-diagramdata
"""

import argparse
import base64
import json
import os
import re
import ssl
import sys
import urllib.request
import urllib.error

DEFAULT_CONFLUENCE_BASE = os.getenv("CONFLUENCE_BASE_URL", "https://your-company.atlassian.net/wiki")
DEFAULT_TOKEN = os.getenv("CONFLUENCE_TOKEN", "")

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def get_page_details(page_id, base_url=DEFAULT_CONFLUENCE_BASE, token=DEFAULT_TOKEN, expand="version,body.storage"):
    url = f"{base_url}/rest/api/content/{page_id}?expand={expand}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    ctx = get_ssl_context()
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_existing_attachments(page_id, base_url=DEFAULT_CONFLUENCE_BASE, token=DEFAULT_TOKEN):
    url = f"{base_url}/rest/api/content/{page_id}/child/attachment"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    ctx = get_ssl_context()
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {att.get("title"): att.get("id") for att in data.get("results", [])}
    except Exception:
        return {}

def upload_single_attachment(page_id, file_path, filename, content_type, base_url=DEFAULT_CONFLUENCE_BASE, token=DEFAULT_TOKEN, existing_id=None):
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    boundary = "----WebKitFormBoundaryGemiConfluenceDrawio"
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    body.extend(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
    body.extend(file_bytes)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    if existing_id:
        url = f"{base_url}/rest/api/content/{page_id}/child/attachment/{existing_id}/data"
    else:
        url = f"{base_url}/rest/api/content/{page_id}/child/attachment"

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "X-Atlassian-Token": "nocheck",
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        },
        method="POST"
    )

    ctx = get_ssl_context()
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read().decode("utf-8"))

def upload_attachments(page_id, xml_or_mxfile_path, png_path, diagram_name, base_url=DEFAULT_CONFLUENCE_BASE, token=DEFAULT_TOKEN):
    """
    Uploads dual attachments to Confluence:
    1. {diagram_name} (content-type: application/vnd.jgraph.mxfile) - NO extension!
    2. {diagram_name}.png (content-type: image/png)
    Automatically updates existing attachments if they already exist.
    """
    if not os.path.exists(xml_or_mxfile_path):
        raise FileNotFoundError(f"Diagram file not found: {xml_or_mxfile_path}")
    if not os.path.exists(png_path):
        raise FileNotFoundError(f"PNG file not found: {png_path}")

    existing = get_existing_attachments(page_id, base_url, token)
    png_filename = f"{diagram_name}.png"

    try:
        # Part 1: mxfile
        res_xml = upload_single_attachment(page_id, xml_or_mxfile_path, diagram_name, "application/vnd.jgraph.mxfile", base_url, token, existing.get(diagram_name))
        xml_ver = res_xml.get("version", {}).get("number", "new")
        print(f"✅ Uploaded/Updated diagram {diagram_name} (v{xml_ver}) on page {page_id}")

        # Part 2: png
        res_png = upload_single_attachment(page_id, png_path, png_filename, "image/png", base_url, token, existing.get(png_filename))
        png_ver = res_png.get("version", {}).get("number", "new")
        print(f"✅ Uploaded/Updated image {png_filename} (v{png_ver}) on page {page_id}")

        return {"xml_version": xml_ver, "png_version": png_ver}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"❌ Attachment upload failed (HTTP {e.code}): {err_msg}", file=sys.stderr)
        raise

def set_macro_revision(page_id, diagram_name, revision, base_url=DEFAULT_CONFLUENCE_BASE, token=DEFAULT_TOKEN):
    """
    Pinpoint updates the <ac:parameter ac:name="revision"> parameter in storage XML
    for a specific Draw.io diagram macro, eliminating the 'Stuck Revision' trap.
    """
    page_data = get_page_details(page_id, base_url, token, expand="version,body.storage")
    current_version = page_data["version"]["number"]
    page_title = page_data["title"]
    storage = page_data["body"]["storage"]["value"]

    # Match the specific drawio macro containing diagramName
    macro_pattern = re.compile(
        rf'(<ac:structured-macro ac:name="drawio"[^>]*>.*?<ac:parameter ac:name="diagramName">{re.escape(diagram_name)}</ac:parameter>.*?</ac:structured-macro>)',
        re.DOTALL
    )

    match = macro_pattern.search(storage)
    if not match:
        raise ValueError(f"Could not locate Draw.io macro for diagram '{diagram_name}' on page {page_id}.")

    old_macro = match.group(1)
    rev_pattern = re.compile(r'<ac:parameter ac:name="revision">\d+</ac:parameter>')
    if rev_pattern.search(old_macro):
        new_macro = rev_pattern.sub(f'<ac:parameter ac:name="revision">{revision}</ac:parameter>', old_macro)
    else:
        # If revision was omitted, insert it before closing tag
        new_macro = old_macro.replace('</ac:structured-macro>', f'<ac:parameter ac:name="revision">{revision}</ac:parameter></ac:structured-macro>')

    new_storage = storage.replace(old_macro, new_macro, 1)

    update_payload = {
        "id": str(page_id),
        "type": "page",
        "title": page_title,
        "version": {
            "number": current_version + 1,
            "message": f"Update Draw.io macro {diagram_name} to revision {revision}"
        },
        "body": {
            "storage": {
                "value": new_storage,
                "representation": "storage"
            }
        }
    }

    url = f"{base_url}/rest/api/content/{page_id}"
    req = urllib.request.Request(
        url,
        data=json.dumps(update_payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="PUT"
    )

    ctx = get_ssl_context()
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print(f"✅ Successfully set revision={revision} for {diagram_name} on page {page_id} (Page v{res['version']['number']})!")
            return res
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"❌ Failed setting revision (HTTP {e.code}): {err_msg}", file=sys.stderr)
        raise

def inject_diagram_macro(page_id, diagram_name, diagram_type="activity", expand_title=None,
                         section_heading=None, intro_text=None, diagram_width=None,
                         diagram_height=None, display_width=None, revision=1,
                         base_url=DEFAULT_CONFLUENCE_BASE, token=DEFAULT_TOKEN):
    """
    Safely embeds the Expand + Draw.io macro into the target section of the Confluence page.
    Supports both 'activity' and 'arch' types with their respective architectural standards.
    """
    if diagram_type == "arch":
        section_heading = section_heading or "<h2>Architecture Diagram</h2>"
        expand_title = expand_title or "Click here to show architecture diagram..."
        intro_text = intro_text or ""
        diagram_width = diagram_width or 521
        diagram_height = diagram_height or 508
        display_width_param = ""
    else: # activity
        section_heading = section_heading or "<h2>Activity Diagram</h2>"
        expand_title = expand_title or "acitivy-diagram"
        intro_text = intro_text or "Perubahan pada section yg berwarna merah"
        diagram_width = diagram_width or 2300
        diagram_height = diagram_height or 4280
        display_width = display_width or 800
        display_width_param = f'<ac:parameter ac:name="width">{display_width}</ac:parameter>'

    page_data = get_page_details(page_id, base_url, token, expand="version,body.storage")
    current_version = page_data["version"]["number"]
    page_title = page_data["title"]
    storage = page_data["body"]["storage"]["value"]

    intro_html = f"<p>{intro_text}</p>" if intro_text else ""
    macro_xml = (
        f"{section_heading}{intro_html}"
        f'<ac:structured-macro ac:name="expand" ac:schema-version="1">'
        f'<ac:parameter ac:name="title">{expand_title}</ac:parameter>'
        f'<ac:rich-text-body><p>'
        f'<ac:structured-macro ac:name="drawio" ac:schema-version="1">'
        f'<ac:parameter ac:name="border">true</ac:parameter>'
        f'<ac:parameter ac:name="diagramName">{diagram_name}</ac:parameter>'
        f'<ac:parameter ac:name="simpleViewer">false</ac:parameter>'
        f'{display_width_param}'
        f'<ac:parameter ac:name="links">auto</ac:parameter>'
        f'<ac:parameter ac:name="tbstyle">top</ac:parameter>'
        f'<ac:parameter ac:name="lbox">true</ac:parameter>'
        f'<ac:parameter ac:name="diagramWidth">{diagram_width}</ac:parameter>'
        f'<ac:parameter ac:name="height">{diagram_height}</ac:parameter>'
        f'<ac:parameter ac:name="revision">{revision}</ac:parameter>'
        f'</ac:structured-macro>'
        f'</p></ac:rich-text-body>'
        f'</ac:structured-macro><p><br /></p>'
    )

    pattern = re.compile(
        re.escape(section_heading) + r'(?:(?!<h2>).)*?(?=(?:<h2>|<h1>|</ac:layout-cell>))',
        re.DOTALL
    )

    if pattern.search(storage):
        new_storage = pattern.sub(macro_xml, storage, count=1)
    else:
        placeholder = f"{section_heading}<p><br /></p><p><br /></p>"
        if placeholder in storage:
            new_storage = storage.replace(placeholder, macro_xml, 1)
        else:
            raise ValueError(f"Could not locate target section heading '{section_heading}' in page storage.")

    new_version = current_version + 1
    update_payload = {
        "id": str(page_id),
        "type": "page",
        "title": page_title,
        "version": {
            "number": new_version,
            "message": f"Inject {diagram_type} diagram macro ({diagram_name})"
        },
        "body": {
            "storage": {
                "value": new_storage,
                "representation": "storage"
            }
        }
    }

    url = f"{base_url}/rest/api/content/{page_id}"
    req = urllib.request.Request(
        url,
        data=json.dumps(update_payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="PUT"
    )

    ctx = get_ssl_context()
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print(f"✅ Successfully updated Confluence page {page_id} to Version {res['version']['number']}!")
            return res
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"❌ Confluence page update failed (HTTP {e.code}): {err_msg}", file=sys.stderr)
        raise

def verify_page_view(page_id, base_url=DEFAULT_CONFLUENCE_BASE, token=DEFAULT_TOKEN):
    """
    Verifies that the page view renders expand and drawio macros without errors,
    and inspects base64 data-diagramdata to ensure active revision and preview match.
    """
    page_data = get_page_details(page_id, base_url, token, expand="body.view")
    view_html = page_data.get("body", {}).get("view", {}).get("value", "")
    has_expand = "expand-control-text" in view_html
    has_drawio = 'data-macro-name="drawio"' in view_html or "drawio-macro" in view_html

    print(f"🔍 Verification Results for Page {page_id}:")
    print(f"   - Expand Macro Rendered : {'YES' if has_expand else 'NO'}")
    print(f"   - Draw.io Macro Rendered: {'YES' if has_drawio else 'NO'}")

    datas = re.findall(r'data-diagramdata="([^"]+)"', view_html)
    if datas:
        print("\n📊 Active Rendered Draw.io Macros on Page:")
        for idx, b64 in enumerate(datas):
            try:
                dec = json.loads(base64.b64decode(b64).decode("utf-8"))
                d_name = dec.get("diagramName")
                d_rev = dec.get("revision")
                d_w = dec.get("width")
                d_prev = dec.get("previewName")
                print(f"   [{idx+1}] Name: {d_name} | Rev: {d_rev} | Width: {d_w} | Preview: {d_prev}")
            except Exception as e:
                print(f"   [{idx+1}] Unable to decode data-diagramdata: {e}")

    return has_expand and has_drawio

def main():
    parser = argparse.ArgumentParser(description="Confluence Draw.io Diagram Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: upload
    p_upload = subparsers.add_parser("upload", help="Upload dual attachments (mxfile + png) to Confluence")
    p_upload.add_argument("--page-id", required=True, help="Confluence Page ID")
    p_upload.add_argument("--xml", required=True, help="Path to diagram XML / mxfile")
    p_upload.add_argument("--png", required=True, help="Path to rendered PNG")
    p_upload.add_argument("--name", required=True, help="Diagram name in Confluence (without extension)")
    p_upload.add_argument("--token", default=DEFAULT_TOKEN, help="Bearer token")

    # Subcommand: set-revision
    p_setrev = subparsers.add_parser("set-revision", help="Pinpoint update macro revision in page storage")
    p_setrev.add_argument("--page-id", required=True, help="Confluence Page ID")
    p_setrev.add_argument("--name", required=True, help="Diagram name in Confluence")
    p_setrev.add_argument("--revision", type=int, required=True, help="Target revision number (e.g. 2, 3)")
    p_setrev.add_argument("--token", default=DEFAULT_TOKEN, help="Bearer token")

    # Subcommand: inject
    p_inject = subparsers.add_parser("inject", help="Inject expand + drawio macro into Confluence page")
    p_inject.add_argument("--page-id", required=True, help="Confluence Page ID")
    p_inject.add_argument("--name", required=True, help="Diagram name (attachment title)")
    p_inject.add_argument("--type", choices=["activity", "arch"], default="activity", help="Diagram type (activity / arch)")
    p_inject.add_argument("--title", help="Title of expand macro")
    p_inject.add_argument("--heading", help="Target HTML section heading")
    p_inject.add_argument("--intro", help="Introductory paragraph above expand")
    p_inject.add_argument("--width", type=int, help="Canvas width (default 2300 for activity, 521 for arch)")
    p_inject.add_argument("--height", type=int, help="Canvas height (default 4280 for activity, 508 for arch)")
    p_inject.add_argument("--display-width", type=int, default=800, help="Display width for viewer")
    p_inject.add_argument("--revision", type=int, default=1, help="Initial revision number")
    p_inject.add_argument("--token", default=DEFAULT_TOKEN, help="Bearer token")

    # Subcommand: publish (one-shot: upload + inject + verify)
    p_pub = subparsers.add_parser("publish", help="One-shot upload, inject, and verify")
    p_pub.add_argument("--page-id", required=True, help="Confluence Page ID")
    p_pub.add_argument("--xml", required=True, help="Path to diagram XML / mxfile")
    p_pub.add_argument("--png", required=True, help="Path to rendered PNG")
    p_pub.add_argument("--name", required=True, help="Diagram name in Confluence (without extension)")
    p_pub.add_argument("--type", choices=["activity", "arch"], default="activity", help="Diagram type")
    p_pub.add_argument("--title", help="Title of expand macro")
    p_pub.add_argument("--heading", help="Target HTML section heading")
    p_pub.add_argument("--intro", help="Introductory paragraph above expand")
    p_pub.add_argument("--width", type=int, help="Canvas width")
    p_pub.add_argument("--height", type=int, help="Canvas height")
    p_pub.add_argument("--display-width", type=int, default=800, help="Display width")
    p_pub.add_argument("--token", default=DEFAULT_TOKEN, help="Bearer token")

    # Subcommand: verify
    p_ver = subparsers.add_parser("verify", help="Verify view HTML of page and list active diagrams")
    p_ver.add_argument("--page-id", required=True, help="Confluence Page ID")
    p_ver.add_argument("--token", default=DEFAULT_TOKEN, help="Bearer token")

    args = parser.parse_args()

    if args.command == "upload":
        upload_attachments(args.page_id, args.xml, args.png, args.name, token=args.token)
    elif args.command == "set-revision":
        set_macro_revision(args.page_id, args.name, args.revision, token=args.token)
    elif args.command == "inject":
        inject_diagram_macro(args.page_id, args.name, diagram_type=args.type, expand_title=args.title,
                             section_heading=args.heading, intro_text=args.intro,
                             diagram_width=args.width, diagram_height=args.height,
                             display_width=args.display_width, revision=args.revision,
                             token=args.token)
    elif args.command == "publish":
        upload_res = upload_attachments(args.page_id, args.xml, args.png, args.name, token=args.token)
        rev = upload_res.get("xml_version") if isinstance(upload_res.get("xml_version"), int) else 1
        inject_diagram_macro(args.page_id, args.name, diagram_type=args.type, expand_title=args.title,
                             section_heading=args.heading, intro_text=args.intro,
                             diagram_width=args.width, diagram_height=args.height,
                             display_width=args.display_width, revision=rev,
                             token=args.token)
        verify_page_view(args.page_id, token=args.token)
    elif args.command == "verify":
        verify_page_view(args.page_id, token=args.token)

if __name__ == "__main__":
    main()
