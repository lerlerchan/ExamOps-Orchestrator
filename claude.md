# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Summary

ExamOps Orchestrator is an AI-powered **5-step exam creation pipeline** for Southern University College. It takes a lecturer from raw syllabus and learning materials through AI-assisted question generation, CLO/PLO moderation, and finally automated exam paper formatting — all in a single web interface.

Steps: **Upload Syllabus → Upload Materials → Copilot (Question Generation) → Moderation Form → Format Exam Paper**

Full architecture and design decisions are in [`claude.md`](./claude.md). Full product requirements are in [`PRD.md`](./PRD.md). Sample template guidelines are in `sample/`.

> **Status**: Core formatting pipeline deployed on Azure Functions. 5-step wizard UI and new agents are under active development (hackathon submission: AI Dev Days, Feb 10 – Mar 15 2026).

---

## Tech Stack

- **Python 3.11+** — primary language
- **python-docx** — `.docx` manipulation
- **Semantic Kernel** — multi-agent orchestration (Microsoft Agent Framework)
- **Azure Functions** — serverless HTTP trigger entry point
- **Azure Blob Storage** — file I/O (containers: `examops-input`, `examops-output`, `examops-templates`)
- **Azure Table Storage** — session persistence across wizard steps (`ExamSession` model)
- **Azure AI Search** — vector DB for template rules retrieval + RAG over learning materials
- **Azure OpenAI GPT-4o-mini** via **Azure AI Foundry** — CLO extraction, LLM validation, RAG chat
- **Azure Bot Framework SDK** — Microsoft Teams bot
- **MCP SDK (Python)** — `mcp` package; exposes ExamOps pipeline as callable MCP tools
- **Server-Sent Events (SSE)** — streaming chat responses in Step 3

---

## Repository Structure

```
src/
├── agents/
│   ├── coordinator_agent/         # Orchestrator — session lifecycle + sub-agent routing
│   ├── file_handler_agent/        # Blob Storage CRUD + SharePoint download via Graph API
│   ├── formatting_engine/         # Hybrid: Rule-Based (python-docx) + LLM validator
│   ├── diff_generator/            # HTML + Word diff reports
│   ├── syllabus_agent/            # NEW: CLO/PLO extraction from uploaded syllabus
│   ├── question_copilot_agent/    # NEW: Streaming RAG chat; questions aligned to CLOs
│   └── moderation_form_agent/     # NEW: Fill AARO-FM-030 .docx template
├── mcp/
│   └── server.py                  # NEW: MCP server exposing ExamOps as callable tools
├── functions/
│   ├── format_exam/               # Existing: POST /api/format-exam
│   ├── serve_web/                 # Existing: GET /api/web
│   ├── upload_syllabus/           # NEW: POST /api/upload-syllabus
│   ├── upload_materials/          # NEW: POST /api/upload-materials
│   ├── chat/                      # NEW: POST /api/chat (SSE streaming)
│   ├── fill_moderation_form/      # NEW: POST /api/fill-moderation-form
│   └── export_questions/          # NEW: POST /api/export-questions
├── session/
│   └── session_store.py           # NEW: Azure Table Storage session CRUD
├── utils/
│   ├── template_retrieval.py      # Azure AI Search vector queries
│   ├── docx_parser.py             # Document parsing helpers
│   └── validation.py              # LLM validation prompts + calls
└── web/
    └── index.html                 # 5-step wizard UI (SSE chat, step nav, diff viewer)
tests/
templates/
scripts/
  └── upload_template.py           # AI Search ingestion script
requirements.txt
```

---

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run a single test
pytest tests/test_formatting_engine.py::test_numbering_correction -v

# Run Azure Function locally
cd src/functions
func start

# Deploy to Azure Functions
func azure functionapp publish examops-functions

# Lint
flake8 src/ tests/
```

---

## Orchestrator Workflow

When given a task, follow this orchestration pattern:

### Step 1 — Break into subtasks

Analyse the task and split it into backend subtasks and frontend subtasks. A subtask should be atomic (one concern, one file or one function), have a clear acceptance criterion, and be independent enough to execute without waiting on a sibling subtask.

### Step 2 — Write task files

Write the subtasks to their respective files **before doing any implementation**:

- `tasks/backend.md` — backend subtasks (agents, Azure Functions, python-docx logic, API routes, DB queries)
- `tasks/frontend.md` — frontend subtasks (Teams Bot messages, HTML diff report, any UI)

Each file must use this format:

```markdown
## Task: <short title>
**File**: `src/path/to/file.py`
**Goal**: One-sentence description of what done looks like.
**Steps**:
1. ...
2. ...
**Result file**: `tasks/results/<task-slug>.md`
```

Every task must declare a **result file** path. That file is written by the sub-agent (or you) when the task is complete, containing a brief summary of what was done and any caveats.

### Step 3 — Execute subtasks

Work through the task lists. For each subtask:

1. Implement it.
2. Write the declared result file to `tasks/results/<task-slug>.md`.

Backend and frontend tasks that are truly independent may be executed in parallel (launch as background sub-agents if applicable). Tasks with dependencies must run sequentially.

### Step 4 — Wait for result files before proceeding

Do **not** start a dependent subtask until the result file of its dependency exists. Before moving to integration or the next phase, verify every expected result file is present:

```
tasks/results/
├── <backend-task-slug>.md   ✅
├── <frontend-task-slug>.md  ✅
└── ...
```

If a result file is missing, the subtask is not done — do not proceed past it.

---

## 5-Step Exam Creation Pipeline

```
[Left Panel Navigation]
  Step 1 ● Upload Syllabus
  Step 2 ● Upload Learning Materials
  Step 3 ● Copilot (Question Generation)
  Step 4 ● Moderation Form (CLO/PLO Mapping)
  Step 5 ● Format Exam Paper
```

| Step | User Action | Agent | Output |
|------|-------------|-------|--------|
| 1 | Upload `.docx`/`.pdf` syllabus OR paste SharePoint URL | `SyllabusAgent` | CLO/PLO list stored in session |
| 2 | Upload learning materials OR paste SharePoint URL | `FileHandlerAgent` | Materials in Blob, indexed in AI Search |
| 3 | Free chat with AI copilot; click "Add to Exam" per question | `QuestionCopilotAgent` | Curated question list in session |
| 4 | Review CLO mapping; download moderation form | `ModerationFormAgent` | Filled AARO-FM-030 `.docx` |
| 5 | Upload/paste exam draft; apply formatting | `FormattingEngineAgent` | Formatted exam + HTML diff |

All steps share a `session_id` (UUID) that tracks state in Azure Table Storage.

---

## Session Model

Each exam creation session is identified by a `session_id` (UUID) and stored as a row in **Azure Table Storage** (`ExamSessions` table).

```python
ExamSession:
  session_id: str           # Partition key
  created_at: datetime
  syllabus_url: str         # Blob URL for uploaded syllabus
  clo_list: List[str]       # CLOs extracted by SyllabusAgent
  plo_list: List[str]       # PLOs extracted by SyllabusAgent
  materials_urls: List[str] # Blob URLs for learning materials
  questions: List[dict]     # [{text, clo, marks}] built in Step 3
  moderation_form_url: str  # Blob URL for filled AARO-FM-030 (Step 4)
  formatted_exam_url: str   # Blob URL for formatted exam (Step 5)
  compliance_score: float   # 0–100 from LLM validator
```

`src/session/session_store.py` owns all Table Storage CRUD. The `session_id` is persisted in `localStorage` on the frontend and sent as a header/param on every API call.

---

## Agents

### CoordinatorAgent (`src/agents/coordinator_agent/`)
Orchestrates the full workflow and owns session lifecycle. Single entry point from both the Teams Bot and all Azure Function HTTP triggers. Routes to sub-agents in sequence per step; agents do not call each other directly.

### FileHandlerAgent (`src/agents/file_handler_agent/`)
Azure Blob Storage CRUD for the three containers (`examops-input`, `examops-output`, `examops-templates`) and OneDrive sharing links via Microsoft Graph API. Also retrieves template rules from Azure AI Search for the formatting step.

**SharePoint integration**: `download_from_sharepoint(sharepoint_url: str) -> bytes` resolves a SharePoint file URL to raw bytes using Graph API credentials (`GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`). Called by Steps 1 and 2 when the user pastes a SharePoint URL instead of uploading a file.

### FormattingEngineAgent (`src/agents/formatting_engine/`)
Two-layer hybrid — do not merge the layers:

- **Layer 1 — Rule-Based** (`RuleBasedFormatter`): Deterministic python-docx transforms: header/footer injection, numbering correction (`Q1.` → `(a)` → `(i)`), marks notation `(3 marks)`, colon spacing (`DATE :` → `DATE : `), indentation (`Tab 0.5 × 3 = 1.5cm` level 2, `× 6 = 3.0cm` level 3).
- **Layer 2 — LLM Validation** (`LLMValidator`): GPT-4o-mini via Azure Foundry — runs after Layer 1, handles ambiguous numbering edge cases, preserves `m:oMath` XML runs (never reformat equation content), returns a compliance score 0–100%.

Template rules are fetched from Azure AI Search at runtime, not hardcoded. Upload scripts live in `scripts/upload_template.py`.

### DiffGeneratorAgent (`src/agents/diff_generator/`)
Produces a color-coded HTML diff (deletions red, additions green) using `difflib.HtmlDiff` and a summary stats dict: `{numbering_fixes, spacing_fixes, formatting_fixes, compliance_score}`. Delivered to the Teams Bot as an inline card.

### SyllabusAgent (`src/agents/syllabus_agent/syllabus_agent.py`) — NEW
Accepts a `.docx` or `.pdf` syllabus (bytes) and uses GPT-4o via Azure Foundry to extract structured CLO and PLO lists. Returns `{"clo_list": [...], "plo_list": [...]}` and writes the result to the session. Called by the `/api/upload-syllabus` function.

### QuestionCopilotAgent (`src/agents/question_copilot_agent/question_copilot_agent.py`) — NEW
Streaming RAG chat agent. Uses Azure AI Search over indexed learning materials to ground responses. Streams answer tokens via SSE. Each response includes a suggested CLO mapping and marks value so the user can click "Add to Exam" to append to `session.questions`. Called by `/api/chat`.

### ModerationFormAgent (`src/agents/moderation_form_agent/moderation_form_agent.py`) — NEW
Reads `session.questions` and `session.clo_list`/`plo_list`, fills the AARO-FM-030 `.docx` template with question text, CLO, PLO, and marks columns, uploads the completed form to Blob Storage, and returns the download URL. Called by `/api/fill-moderation-form`.

---

## MCP Server

`src/mcp/server.py` exposes the ExamOps pipeline as callable MCP tools, satisfying the hackathon requirement for MCP / A2A protocols.

**Exposed tools:**

| Tool | Signature | Returns |
|------|-----------|---------|
| `upload_syllabus` | `(file_path_or_sharepoint_url: str) -> dict` | `{session_id, clo_list, plo_list}` |
| `generate_questions` | `(session_id: str, prompt: str) -> list` | List of question suggestions |
| `fill_moderation_form` | `(session_id: str) -> str` | Blob download URL |
| `format_exam` | `(session_id: str) -> dict` | `{formatted_exam_url, compliance_score}` |

The MCP server can be run standalone (`python -m src.mcp.server`) or registered with any MCP-compatible host (Claude Desktop, Copilot Studio, etc.).

---

## Azure Functions (API Endpoints)

| Function | Endpoint | Method | Notes |
|----------|----------|--------|-------|
| `format_exam` | `/api/format-exam` | POST multipart | Existing |
| `serve_web` | `/api/web` | GET | Existing — serves `index.html` |
| `upload_syllabus` | `/api/upload-syllabus` | POST multipart | File or `sharepoint_url` param |
| `upload_materials` | `/api/upload-materials` | POST multipart | File or `sharepoint_url` param |
| `chat` | `/api/chat` | POST JSON | SSE streaming response |
| `fill_moderation_form` | `/api/fill-moderation-form` | POST JSON | `{session_id}` |
| `export_questions` | `/api/export-questions` | POST JSON | Returns `.docx` blob URL for Step 5 |

---

## Web UI — 5-Step Wizard

`src/web/index.html` — single-file wizard with:

- **Left panel**: Step list with status indicators (pending / active / complete)
- **Main area**: Step-specific view per step
- **Step 3 layout**: Chat panel (left) + Question List sidebar (right) with "Add to Exam" per response
- **Streaming**: `EventSource` SSE for Step 3 chat responses
- **Session persistence**: `localStorage` stores `session_id`; sent as `X-Session-ID` header on all API calls

---

## Hackathon Alignment (AI Dev Days 2026)

| Criterion | Implementation |
|-----------|---------------|
| Real-world impact | Saves lecturers 4–6 hrs/exam × hundreds of papers per year |
| Microsoft Agent Framework | Semantic Kernel orchestration across 6 agents |
| Multi-agent systems | CoordinatorAgent → 5 specialised sub-agents |
| MCP server | `src/mcp/server.py` exposing ExamOps as callable tools |
| Azure AI Foundry | GPT-4o-mini via Azure Foundry for CLO extraction + LLM validation |
| Azure AI Search | RAG over learning materials for question generation |
| Microsoft Graph API | SharePoint download + OneDrive sharing links |
| Azure Functions | Serverless HTTP triggers for all pipeline steps |
| Enterprise scalability | Multi-campus templates via AI Search vector DB |
