# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Summary

ExamOps Orchestrator is an AI-powered exam paper formatting system for Southern University College. It automates fixing numbering (Q1. → (a) → (i)), spacing, margins, marks notation, and headers in `.docx` exam papers to comply with institutional templates.

Full architecture and design decisions are in [`claude.md`](./claude.md). Full product requirements are in [`PRD.md`](./PRD.md). Sample template guidelines are in `sample/`.

> **Status**: Greenfield — no source code exists yet. This is the planned structure.

---

## Tech Stack

- **Python 3.11+** — primary language
- **python-docx** — `.docx` manipulation
- **Semantic Kernel** — multi-agent orchestration (Microsoft Agent Framework)
- **Azure Functions** — serverless HTTP trigger entry point
- **Azure Blob Storage** — file I/O (containers: `examops-input`, `examops-output`, `examops-templates`)
- **Azure AI Search** — vector DB for template rules retrieval
- **Azure OpenAI GPT-4o-mini** via **Azure AI Foundry** — LLM validation layer
- **Azure Bot Framework SDK** — Microsoft Teams bot

---

## Planned Repository Structure

```
src/
├── agents/
│   ├── coordinator_agent.py      # Orchestrator — entry point, routes to sub-agents
│   ├── file_handler_agent.py     # Azure Blob Storage + OneDrive via Graph API
│   ├── formatting_engine.py      # Hybrid: Rule-Based (python-docx) + LLM validator
│   └── diff_generator.py         # HTML + Word diff reports
├── utils/
│   ├── template_retrieval.py     # Azure AI Search vector queries
│   ├── docx_parser.py            # Document parsing helpers
│   └── validation.py             # LLM validation prompts + calls
├── functions/
│   └── format_exam/              # Azure Function HTTP trigger
│       ├── __init__.py
│       └── function.json
└── bot/
    ├── bot.py                    # Teams Bot ActivityHandler
    └── app.py                    # Bot Framework adapter
tests/
templates/
requirements.txt
```

---

## Development Commands

Once source code is created:

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

## Agents

### CoordinatorAgent (`src/agents/coordinator_agent.py`)
Orchestrates the full workflow and owns job state. Single entry point from both the Teams Bot and the Azure Function HTTP trigger. Calls agents in sequence: `FileHandlerAgent` → `FormattingEngineAgent` → `DiffGeneratorAgent`. Agents do not call each other directly — all routing goes through here.

### FileHandlerAgent (`src/agents/file_handler_agent.py`)
Azure Blob Storage CRUD for the three containers (`examops-input`, `examops-output`, `examops-templates`) and OneDrive sharing links via Microsoft Graph API. Also retrieves template rules from Azure AI Search for the formatting step.

### FormattingEngineAgent (`src/agents/formatting_engine.py`)
Two-layer hybrid — do not merge the layers:

- **Layer 1 — Rule-Based** (`RuleBasedFormatter`): Deterministic python-docx transforms: header/footer injection, numbering correction (`Q1.` → `(a)` → `(i)`), marks notation `(3 marks)`, colon spacing (`DATE :` → `DATE : `), indentation (`Tab 0.5 × 3 = 1.5cm` level 2, `× 6 = 3.0cm` level 3).
- **Layer 2 — LLM Validation** (`LLMValidator`): GPT-4o-mini via Azure Foundry — runs after Layer 1, handles ambiguous numbering edge cases, preserves `m:oMath` XML runs (never reformat equation content), returns a compliance score 0–100%.

Template rules are fetched from Azure AI Search at runtime, not hardcoded. Upload scripts live in `scripts/upload_template.py`.

### DiffGeneratorAgent (`src/agents/diff_generator.py`)
Produces a color-coded HTML diff (deletions red, additions green) using `difflib.HtmlDiff` and a summary stats dict: `{numbering_fixes, spacing_fixes, formatting_fixes, compliance_score}`. Delivered to the Teams Bot as an inline card.
