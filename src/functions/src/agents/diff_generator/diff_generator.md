# DiffGeneratorAgent

**File**: `src/agents/diff_generator/diff_generator.py`

---

## Purpose

Produces a color-coded HTML diff report and a summary statistics dict from before/after document pairs. The output is consumed by the Teams Bot as an inline card attachment and stored in Azure Blob Storage.

---

## Outputs

### 1. HTML Diff Report (`html_report`)

A complete HTML document built with `difflib.HtmlDiff(wrapcolumn=80)`.

Structure:
```
<!DOCTYPE html>
<html>
  <head>
    <title>ExamOps Diff Report</title>
    <style>... ExamOps CSS ...</style>
  </head>
  <body>
    <div> Summary header (score + change counts) </div>
    <table class="diff"> difflib output </table>
  </body>
</html>
```

### 2. Summary Stats Dict (`summary_stats`)

```json
{
  "numbering_fixes":        3,
  "spacing_fixes":          2,
  "mark_formatting_fixes":  1,
  "indentation_fixes":      4,
  "header_footer_added":    true,
  "total_changes":         11,
  "compliance_score":      94.5
}
```

`compliance_score` is taken directly from the `LLMValidator` result (may be `null` if LLM timed out).

---

## Teams Card Display Format

The Teams Bot renders the diff report as an **Adaptive Card** with:

- Compliance score badge (green ≥ 90, amber 70–89, red < 70)
- Total changes count
- Breakdown list (numbering / spacing / marks / indentation / header)
- "View full report" button → links to `diff_url` (Azure Blob HTML)

---

## Color Coding Scheme

| Change type | Background | Text |
|-------------|-----------|------|
| Deletion (removed) | `#ffc7ce` red | `#9c0006` |
| Addition (inserted) | `#c6efce` green | `#276221` |
| Change (modified) | `#ffeb9c` amber | `#9c6500` |
| Unchanged context | white | black |

Implemented via CSS `span.diff_add`, `span.diff_sub`, `span.diff_chg`.

---

## Method Reference

### `create_html_diff(original_doc, formatted_doc, validation) -> dict`

Main entry point. Extracts text from both documents, generates `difflib.HtmlDiff` table with 3 lines of context, injects summary header and CSS, returns `{html_report, summary_stats}`.

### `generate_summary_stats(original_doc, formatted_doc, validation) -> dict`

Counts fixes by category using `re.search` against `validation["issues_found"]` strings. Detects header addition by comparing first-section header text between original and formatted.

### `_extract_text_with_formatting(doc) -> str`

Returns `"\n".join(para.text for para in doc.paragraphs)`. Blank paragraphs produce blank lines, preserving visual separation between questions.

### `_add_css_styling(html) -> str`

Final-pass guard: injects `_DIFF_CSS` block before `</head>` if no `<style>` tag is present.
