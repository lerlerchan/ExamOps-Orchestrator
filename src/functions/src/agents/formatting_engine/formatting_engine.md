# FormattingEngineAgent

**File**: `src/agents/formatting_engine/formatting_engine.py`

---

## Purpose

Two-layer hybrid document formatter for exam papers. The two layers are kept as separate classes and must **never be merged**.

---

## Two-Layer Architecture

```
FormattingEngineAgent.process_and_validate(original, template_rules)
    │
    ├─ Layer 1: RuleBasedFormatter.process(doc, template_rules)
    │   Deterministic python-docx transforms — fast, always runs
    │
    └─ Layer 2: LLMValidator.validate(original, formatted, template_rules)
        GPT-4o-mini — handles edge cases, returns compliance score
        Falls back gracefully on timeout/error
```

**Rationale**: Rule-based transforms are deterministic and fast, making them the core workhorse. The LLM layer adds intelligence for ambiguous cases without blocking the pipeline if unavailable.

---

## Layer 1 — Rule Table

| Rule | Input example | Output example |
|------|--------------|----------------|
| Header/footer injection | *(missing)* | `SOUTHERN UNIVERSITY COLLEGE` |
| Page margins | Any | top/bottom 2.5 cm, left 3.0 cm, right 2.5 cm |
| Numbering — Q-level | `Q1)` | `Q1.` |
| Numbering — sub-level | `1a)` | `(a)` |
| Numbering — sub-sub | `1.a.i` | `(a)(i)` style normalisation |
| Marks notation | `[3 marks]`, `(3 Marks)` | `(3 marks)` |
| Colon spacing | `DATE :` | `DATE : ` |
| Indentation L1 | `Q1.` paragraph | 0 cm |
| Indentation L2 | `(a)` paragraph | 1.5 cm |
| Indentation L3 | `(i)` paragraph | 3.0 cm |

---

## m:oMath Preservation Rule

**Any paragraph whose XML tree contains an `m:oMath` element is skipped entirely by `_fix_numbering`, `_format_marks`, `_enforce_spacing`, and `_fix_indentation`.**

Math expressions are identified at the run level using `qn("m:oMath")`. This ensures Word's equation objects (`<m:oMath>...</m:oMath>`) are never corrupted by text replacement.

---

## Layer 2 — LLM Prompt Structure

**System prompt** (fixed):
> "You are an exam paper compliance checker for Southern University College. Evaluate the formatted document against the template rules and return a JSON object with the following keys: compliance_score (0-100), category_scores (dict), issues_found (list of str), edge_cases (list of str), math_expressions_preserved (bool), summary (str). Respond with JSON only — no markdown fences."

**User prompt** (runtime):
```
TEMPLATE RULES:
{ ... json ... }

ORIGINAL DOCUMENT:
<first 4000 chars of original>

FORMATTED DOCUMENT:
<first 4000 chars of formatted>
```

**Model**: `gpt-4o-mini` via `AIProjectClient` at `AZURE_FOUNDRY_ENDPOINT`
**Temperature**: `0.1` (near-deterministic)
**Timeout**: 30 seconds

---

## LLM Response Schema

```json
{
  "compliance_score": 94.5,
  "category_scores": {
    "numbering": 100,
    "spacing": 90,
    "marks": 95,
    "header": 100,
    "indent": 88
  },
  "issues_found": ["Q3(b)(ii) indentation incorrect"],
  "edge_cases": ["Mixed Roman/Arabic sub-numbering in Q5"],
  "math_expressions_preserved": true,
  "summary": "Document is 94.5% compliant with minor indentation issues.",
  "fallback_mode": false
}
```

---

## Fallback Behaviour

On any exception (timeout, network error, parse error):

```json
{
  "compliance_score": null,
  "category_scores": {},
  "issues_found": [],
  "edge_cases": [],
  "math_expressions_preserved": true,
  "summary": "LLM validation unavailable.",
  "fallback_mode": true,
  "error": "<exception message>"
}
```

The pipeline continues with rule-based results. `CoordinatorAgent` sets `status="partial"` when `fallback_mode=True`.

---

## Environment Variables

| Variable | Used By |
|----------|---------|
| `AZURE_FOUNDRY_ENDPOINT` | `LLMValidator` — AIProjectClient endpoint |
| `AZURE_FOUNDRY_KEY` | `LLMValidator` — credential (fallback to `DefaultAzureCredential`) |
