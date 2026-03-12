"""
DiffGeneratorAgent — color-coded HTML diff reports and summary statistics.

Produces:
    html_report   — difflib.HtmlDiff output with injected CSS
    summary_stats — {numbering_fixes, spacing_fixes, mark_formatting_fixes,
                     indentation_fixes, header_footer_added,
                     total_changes, compliance_score}

The HTML report is delivered to the Teams Bot as an inline card attachment.
"""

import difflib
import logging
import re

from docx import Document

logger = logging.getLogger(__name__)

# CSS injected into the diff HTML
_DIFF_CSS = """
<style>
  body { font-family: Consolas, monospace; font-size: 13px; }
  table.diff { border-collapse: collapse; width: 100%; }
  td { padding: 2px 6px; vertical-align: top; }
  .diff_header { background-color: #f0f0f0; font-weight: bold; }
  .diff_next   { background-color: #f0f0f0; }
  span.diff_add { background-color: #c6efce; color: #276221; }
  span.diff_sub { background-color: #ffc7ce; color: #9c0006; }
  span.diff_chg { background-color: #ffeb9c; color: #9c6500; }
</style>
"""


class DiffGeneratorAgent:
    """
    Generates HTML diff reports and summary statistics for Teams cards.

    Color scheme:
        Deletions — red background  (#ffc7ce)
        Additions — green background (#c6efce)
        Changes   — amber background (#ffeb9c)
    """

    def create_html_diff(
        self,
        original_doc: Document,
        formatted_doc: Document,
        validation: dict,
    ) -> dict:
        """
        Build a color-coded HTML diff between original and formatted documents.

        Args:
            original_doc:  Original (unformatted) python-docx Document.
            formatted_doc: Formatted python-docx Document.
            validation:    Validation result dict from LLMValidator.

        Returns:
            dict with keys:
                html_report  — Full HTML string (CSS-styled difflib output)
                summary_stats — Summary dict (see generate_summary_stats)
        """
        original_text = self._extract_text_with_formatting(original_doc)
        formatted_text = self._extract_text_with_formatting(formatted_doc)

        original_lines = original_text.splitlines(keepends=True)
        formatted_lines = formatted_text.splitlines(keepends=True)

        differ = difflib.HtmlDiff(wrapcolumn=80)
        html_table = differ.make_table(
            original_lines,
            formatted_lines,
            fromdesc="Original",
            todesc="Formatted",
            context=True,
            numlines=3,
        )

        summary_stats = self.generate_summary_stats(
            original_doc, formatted_doc, validation
        )
        summary_header = self._build_summary_header(summary_stats)

        full_html = (
            "<!DOCTYPE html>\n<html>\n<head>"
            "<meta charset='utf-8'>"
            "<title>ExamOps Diff Report</title>"
            f"{_DIFF_CSS}"
            "</head>\n<body>\n"
            f"{summary_header}\n"
            f"{html_table}\n"
            "</body>\n</html>"
        )

        styled_html = self._add_css_styling(full_html)
        logger.info(
            "Diff report generated — %d total change(s)",
            summary_stats.get("total_changes", 0),
        )
        return {"html_report": styled_html, "summary_stats": summary_stats}

    def generate_summary_stats(
        self,
        original_doc: Document,
        formatted_doc: Document,
        validation: dict,
    ) -> dict:
        """
        Count fix categories from validation issues and structural changes.

        Categories:
            numbering_fixes       — issues containing "numbering" / "number"
            spacing_fixes         — issues containing "spacing" / "colon"
            mark_formatting_fixes — issues containing "mark"
            indentation_fixes     — issues containing "indent"
            header_footer_added   — True if formatted doc header != original

        Args:
            original_doc:  Original Document.
            formatted_doc: Formatted Document.
            validation:    Validation result dict.

        Returns:
            {
                numbering_fixes,
                spacing_fixes,
                mark_formatting_fixes,
                indentation_fixes,
                header_footer_added,
                total_changes,
                compliance_score,
            }
        """
        issues: list = validation.get("issues_found", [])

        numbering_fixes = sum(
            1 for i in issues if re.search(r"number(ing)?", i, re.IGNORECASE)
        )
        spacing_fixes = sum(
            1 for i in issues if re.search(r"spacing|colon", i, re.IGNORECASE)
        )
        mark_formatting_fixes = sum(
            1 for i in issues if re.search(r"mark", i, re.IGNORECASE)
        )
        indentation_fixes = sum(
            1 for i in issues if re.search(r"indent", i, re.IGNORECASE)
        )

        # Detect header addition by comparing first-section header text
        original_header = self._get_header_text(original_doc)
        formatted_header = self._get_header_text(formatted_doc)
        header_footer_added = original_header != formatted_header

        total_changes = (
            numbering_fixes
            + spacing_fixes
            + mark_formatting_fixes
            + indentation_fixes
            + (1 if header_footer_added else 0)
        )

        return {
            "numbering_fixes": numbering_fixes,
            "spacing_fixes": spacing_fixes,
            "mark_formatting_fixes": mark_formatting_fixes,
            "indentation_fixes": indentation_fixes,
            "header_footer_added": header_footer_added,
            "total_changes": total_changes,
            "compliance_score": validation.get("compliance_score"),
        }

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _extract_text_with_formatting(self, doc: Document) -> str:
        """
        Extract paragraph text joined with newlines.

        Blank lines are preserved between questions (i.e. two consecutive
        empty paragraphs produce a blank line in the output).

        Args:
            doc: python-docx Document.

        Returns:
            Plain-text representation of the document.
        """
        lines = []
        for para in doc.paragraphs:
            lines.append(para.text)
        return "\n".join(lines)

    def _add_css_styling(self, html: str) -> str:
        """
        Ensure the diff HTML has the ExamOps CSS block injected.

        If ``<style>`` is already present (from create_html_diff), this is
        a no-op.  Called as a final pass to guarantee styling.

        Args:
            html: Raw HTML string.

        Returns:
            HTML string with CSS guaranteed to be present.
        """
        if "<style>" in html:
            return html
        return html.replace("</head>", f"{_DIFF_CSS}</head>", 1)

    @staticmethod
    def _get_header_text(doc: Document) -> str:
        """Return the header text of the first section, or empty string."""
        try:
            section = doc.sections[0]
            paras = section.header.paragraphs
            return " ".join(p.text for p in paras).strip()
        except Exception:
            return ""

    @staticmethod
    def _build_summary_header(stats: dict) -> str:
        """Build an HTML summary block for the top of the diff report."""
        score = stats.get("compliance_score")
        score_str = f"{score:.1f}%" if score is not None else "N/A (LLM unavailable)"
        return (
            "<div style='font-family:sans-serif;padding:12px;background:#f8f9fa;"
            "border:1px solid #dee2e6;border-radius:4px;margin-bottom:16px'>"
            f"<h2 style='margin:0 0 8px'>ExamOps Formatting Report</h2>"
            f"<p><strong>Compliance score:</strong> {score_str}</p>"
            f"<p><strong>Total changes:</strong> {stats.get('total_changes', 0)}</p>"
            "<ul>"
            f"<li>Numbering fixes: {stats.get('numbering_fixes', 0)}</li>"
            f"<li>Spacing fixes: {stats.get('spacing_fixes', 0)}</li>"
            f"<li>Mark notation fixes: {stats.get('mark_formatting_fixes', 0)}</li>"
            f"<li>Indentation fixes: {stats.get('indentation_fixes', 0)}</li>"
            f"<li>Header/footer added: {'Yes' if stats.get('header_footer_added') else 'No'}</li>"
            "</ul>"
            "</div>"
        )
