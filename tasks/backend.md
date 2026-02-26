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

---

## Task: Implement Azure Function HTTP Trigger
**File**: `src/functions/format_exam/__init__.py`
**Goal**: HTTP-triggered Azure Function that accepts a `.docx` upload, invokes `CoordinatorAgent`, and returns the job result JSON.
**Steps**:
1. Accept `multipart/form-data` POST with `file` (binary) and `user_id` (string) fields.
2. Upload received bytes to `examops-input` via `FileHandlerAgent.upload_to_blob`.
3. Generate `job_id` (UUID4) and call `CoordinatorAgent.process_job(job_id, user_id, blob_url)`.
4. Return 200 JSON `{job_id, status, compliance_score, formatted_url, diff_url, onedrive_link, summary}` on success.
5. Return 400 for missing fields, 422 for corrupted file, 500 for unexpected errors.
6. Write `function.json` with `httpTrigger` binding, `POST` only, `authLevel: function`.
**Result file**: `tasks/results/azure-function.md`

---

## Task: Implement Teams Bot
**File**: `src/bot/bot.py`, `src/bot/app.py`
**Goal**: Microsoft Teams bot that accepts a `.docx` attachment, triggers the pipeline, and replies with a formatted adaptive card showing results.
**Steps**:
1. In `bot.py` implement `ExamOpsBot(ActivityHandler)` with `on_message_activity`.
2. Detect `.docx` attachment, download it via `attachment.content_url`, upload via `FileHandlerAgent.upload_to_blob`.
3. Reply with "Processing…" card, then call `CoordinatorAgent.process_job`.
4. On completion send adaptive card with: compliance score badge, fix counts (numbering/spacing/formatting), OneDrive link button, diff report link button.
5. Handle no-attachment case: reply with usage instructions.
6. In `app.py` configure `BotFrameworkAdapter` with `MicrosoftAppId`/`MicrosoftAppPassword` from env, wire `/api/messages` route.
**Result file**: `tasks/results/teams-bot.md`

---

## Task: Implement Tests
**File**: `tests/test_formatting_engine.py`, `tests/test_diff_generator.py`, `tests/test_coordinator_agent.py`
**Goal**: Unit tests covering the core formatting transforms, diff generation, and coordinator error paths.
**Steps**:
1. `test_formatting_engine.py` — test `_fix_numbering` (Q1.→(a)→(i)), `_fix_marks_notation`, `_fix_colon_spacing`, `m:oMath` guard skips math runs.
2. `test_diff_generator.py` — test `generate_summary_stats` counts, `_add_css_styling` injects correct CSS, `create_html_diff` returns `html` and `stats` keys.
3. `test_coordinator_agent.py` — test `process_job` success path (mock agents), `ERR_CORRUPTED_FILE`, `ERR_TEMPLATE_NOT_FOUND`, LLM timeout fallback → `status="partial"`.
4. All tests use `pytest` + `pytest-asyncio`; mock Azure SDK calls with `unittest.mock`.
5. Add `tests/__init__.py` and `tests/conftest.py` with shared fixtures (sample docx, mock template_rules).
**Result file**: `tasks/results/tests.md`

---

## Task: Implement SK "Team Leader" CoordinatorAgent
**File**: `src/agents/coordinator_agent/coordinator_agent.py`, `src/agents/job_context.py`, `src/agents/kernel_setup.py`, `src/agents/plugins/`
**Goal**: Replace the hard-coded sequential chain with a `ChatCompletionAgent` team leader that delegates pipeline steps to SK plugins via automatic function calling, with a manual-chain fallback.
**Steps**:
1. Create `src/agents/job_context.py` — `JobContext` dataclass + thread-safe `JobContextRegistry` singleton.
2. Create `src/agents/plugins/__init__.py` (empty package).
3. Create `src/agents/plugins/file_handler_plugin.py` — `FileHandlerPlugin` with 4 `@kernel_function` methods (`download_document`, `get_template`, `save_outputs`, `create_sharing_link`).
4. Create `src/agents/plugins/formatting_plugin.py` — `FormattingPlugin` with `format_and_validate` kernel function.
5. Create `src/agents/plugins/diff_plugin.py` — `DiffPlugin` with `generate_diff` kernel function.
6. Create `src/agents/kernel_setup.py` — `build_kernel()` wires `AzureChatCompletion` + 3 plugins.
7. Refactor `CoordinatorAgent.__init__` to instantiate sub-agents, build kernel, and create `ChatCompletionAgent` team leader (graceful degradation if SK unavailable).
8. Refactor `CoordinatorAgent.process_job` to try SK path first via `_sk_path()`, fall back to original `_manual_chain()` on any exception.
9. Add `TEAM_LEADER_PROMPT` constant with ordered 6-step pipeline instructions.
10. Add `TestSKTeamLeaderPath` and `TestSKFallback` test classes to `tests/test_coordinator_agent.py`.
**Result file**: `tasks/results/team-leader.md`
