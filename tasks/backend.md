# Backend Tasks

## Task: Implement CoordinatorAgent
**File**: `src/agents/coordinator_agent/coordinator_agent.py`
**Goal**: Single-entry orchestrator that drives the full pipeline (download → format → validate → diff → save) and returns a job result dict.
**Steps**:
1. Define `JobState` dataclass with `job_id`, `user_id`, `status`, `file_url`, `created_at`, `updated_at`.
2. Implement `CoordinatorAgent` class with `async def process_job(job_id, user_id, file_url) -> dict`.
3. Call agents in sequence: `FileHandlerAgent` → `FormattingEngineAgent` → `DiffGeneratorAgent`.
4. Handle error cases: corrupted file, template not found, LLM timeout (fallback to rule-based only).
5. Return `{status, compliance_score, formatted_url, diff_url, onedrive_link, summary}`.
6. Write `coordinator_agent.md` spec doc.
**Result file**: `tasks/results/coordinator-agent.md`

---

## Task: Implement FileHandlerAgent
**File**: `src/agents/file_handler_agent/file_handler_agent.py`
**Goal**: Handle all Azure Blob Storage I/O, Azure AI Search vector queries, and OneDrive sharing link creation.
**Steps**:
1. Implement `upload_to_blob(file_stream, filename, user_id) -> str` — uploads to `examops-input`, returns 1-hour SAS URL.
2. Implement `download_from_blob(blob_url) -> Document` — downloads and returns python-docx `Document`.
3. Implement `get_template_from_vectordb(query: str) -> dict` — ada-002 embedding + Azure AI Search.
4. Implement `save_outputs(formatted_doc, diff_html, job_id) -> dict` — saves to `examops-output`, returns URL dict.
5. Implement `create_onedrive_link(blob_url) -> str` — Graph API POST for shareable link.
6. Wire all env vars: `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_KEY`, `AZURE_OPENAI_ENDPOINT`.
7. Write `file_handler_agent.md` spec doc.
**Result file**: `tasks/results/file-handler-agent.md`

---

## Task: Implement FormattingEngineAgent
**File**: `src/agents/formatting_engine/formatting_engine.py`
**Goal**: Two-layer hybrid formatter: deterministic rule-based transforms (Layer 1) followed by GPT-4o-mini LLM validation (Layer 2).
**Steps**:
1. Implement `RuleBasedFormatter.process(doc, template_rules) -> Document` with internal methods for header/footer, margins, numbering, marks, spacing, indentation.
2. Add `m:oMath` XML guard in `_fix_numbering` — skip math expression runs.
3. Implement `LLMValidator.validate(original, formatted, template_rules) -> dict` via `AIProjectClient` at `AZURE_FOUNDRY_ENDPOINT`.
4. Return compliance JSON: `{compliance_score, category_scores, issues_found, edge_cases, math_expressions_preserved, summary}`.
5. Add fallback: on timeout/exception return `{compliance_score: None, fallback_mode: True}`.
6. Implement thin `FormattingEngineAgent.process_and_validate(original, template_rules)` wrapper.
7. Write `formatting_engine.md` spec doc.
**Result file**: `tasks/results/formatting-engine-agent.md`

---

## Task: Implement DiffGeneratorAgent
**File**: `src/agents/diff_generator/diff_generator.py`
**Goal**: Produce a color-coded HTML diff report and a summary stats dict from before/after documents.
**Steps**:
1. Implement `create_html_diff(original_doc, formatted_doc, validation) -> dict` using `difflib.HtmlDiff(wrapcolumn=80)`.
2. Implement `generate_summary_stats(original_doc, formatted_doc, validation) -> dict` — count fixes by category.
3. Implement `_extract_text_with_formatting(doc) -> str` helper.
4. Implement `_add_css_styling(html) -> str` — inject del=red, ins=green CSS.
5. Write `diff_generator.md` spec doc.
**Result file**: `tasks/results/diff-generator-agent.md`
