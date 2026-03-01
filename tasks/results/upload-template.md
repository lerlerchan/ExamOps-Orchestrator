# Result: scripts/upload_template.py

## Status: Complete

## What was done
Implemented `scripts/upload_template.py` — a CLI script that:

1. Parses both sample guideline files:
   - `sample/Exam Paper Format Guideline 1.docx`
   - `sample/Marking Scheme Format Guideline 1.docx`

2. Extracts structured template rules per document:
   - `header_text` — from section header or first uppercase paragraph
   - `footer_text` — from section footer
   - `numbering_scheme` — inferred from paragraph patterns (`Q{n}.`, `(a)`, `(i)`)
   - `marks_pattern` — regex string for marks notation
   - `colon_spacing` — always True
   - `margin_cm` — detected from section margins (EMU → cm conversion)
   - `indentation_cm` — institutional constants (l1=0.0, l2=1.5, l3=3.0)

3. Generates ada-002 embedding from content JSON via Azure OpenAI.

4. Upserts document into Azure AI Search `exam-templates` index with fields:
   - `id`, `title`, `content`, `content_vector`, `template_rules`

## CLI flags
- `--dry-run` — prints extracted rules, skips Azure upload
- `--index-name` — override index name (default: `exam-templates`)

## Dry-run output (verified)
```
Printed 2 template rule document(s).
```
Both guideline files parsed successfully. Numbering scheme `["Q{n}.", "(a)", "(i)"]` correctly detected from both documents.

## Caveats
- Requires `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY` env vars for live upload.
- `--dry-run` mode works without any Azure credentials.
- Header detection falls back to the first all-caps paragraph when the section header is empty or contains course-specific text.
