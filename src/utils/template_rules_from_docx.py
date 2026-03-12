"""
Extract template formatting rules from a python-docx Document.

This is used when the user uploads an example/template .docx in Step 5.
We keep the extracted rules intentionally simple and deterministic:
- margins (cm)
- header/footer first paragraph text
- Normal style base font name/size
- paragraph spacing + line spacing (Normal style)
"""

from __future__ import annotations

from typing import Any


def _emu_to_cm(v: Any) -> float | None:
    try:
        # python-docx Length is EMU-backed; int(v) is EMU
        return round(int(v) / 360000, 2)
    except Exception:
        return None


def extract_template_rules_from_docx(doc) -> dict:
    section = doc.sections[0]

    # Margins
    margin_cm = {
        "top": _emu_to_cm(section.top_margin) or 2.5,
        "bottom": _emu_to_cm(section.bottom_margin) or 2.5,
        "left": _emu_to_cm(section.left_margin) or 3.0,
        "right": _emu_to_cm(section.right_margin) or 2.5,
    }

    # Header/footer text (first paragraph only, for now)
    header_text = ""
    try:
        if section.header and section.header.paragraphs:
            header_text = (section.header.paragraphs[0].text or "").strip()
    except Exception:
        header_text = ""

    footer_text = ""
    try:
        if section.footer and section.footer.paragraphs:
            footer_text = (section.footer.paragraphs[0].text or "").strip()
    except Exception:
        footer_text = ""

    # Normal style typography / spacing
    font_name = None
    font_size_pt = None
    space_before_pt = None
    space_after_pt = None
    line_spacing = None

    try:
        normal = doc.styles["Normal"]
        if normal.font and normal.font.name:
            font_name = normal.font.name
        if normal.font and normal.font.size:
            # Length in EMU -> points (1 pt = 12700 EMU)
            font_size_pt = round(int(normal.font.size) / 12700, 1)
        pf = normal.paragraph_format
        if pf:
            if pf.space_before:
                space_before_pt = round(int(pf.space_before) / 12700, 1)
            if pf.space_after:
                space_after_pt = round(int(pf.space_after) / 12700, 1)
            if pf.line_spacing:
                # Could be float (multiple) or Length; keep as-is
                line_spacing = pf.line_spacing
    except Exception:
        pass

    return {
        "header_text": header_text or "SOUTHERN UNIVERSITY COLLEGE",
        "footer_text": footer_text,
        "margin_cm": margin_cm,
        "base_font": {"name": font_name, "size_pt": font_size_pt},
        "normal_paragraph_format": {
            "space_before_pt": space_before_pt,
            "space_after_pt": space_after_pt,
            "line_spacing": line_spacing,
        },
        # Keep existing defaults for other rules if missing
        "indentation_cm": {"l1": 0.0, "l2": 1.5, "l3": 3.0},
    }

