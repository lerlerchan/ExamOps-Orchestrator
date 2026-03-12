# CoordinatorAgent

**File**: `src/agents/coordinator_agent/coordinator_agent.py`

---

## Purpose

Single entry point for the ExamOps formatting pipeline. Owns job state and drives the full workflow in sequence. Neither the Teams Bot nor the Azure Function HTTP trigger call sub-agents directly — all routing goes through `CoordinatorAgent`.

---

## Entry Points

| Caller | Method |
|--------|--------|
| Azure Function HTTP trigger | `await coordinator.process_job(job_id, user_id, file_url)` |
| Teams Bot ActivityHandler   | `await coordinator.process_job(job_id, user_id, file_url)` |

---

## Sequential Call Chain

```
CoordinatorAgent.process_job()
  │
  ├─ 1. FileHandlerAgent.download_from_blob(file_url)
  │       → original_doc: Document
  │
  ├─ 2. FileHandlerAgent.get_template_from_vectordb(query)
  │       → template_rules: dict
  │
  ├─ 3. FormattingEngineAgent.process_and_validate(original_doc, template_rules)
  │       → (formatted_doc: Document, validation_result: dict)
  │
  ├─ 4. DiffGeneratorAgent.create_html_diff(original_doc, formatted_doc, validation_result)
  │       → diff_result: {html_report, summary_stats}
  │
  ├─ 5. FileHandlerAgent.save_outputs(formatted_doc, html_report, job_id)
  │       → output_urls: {docx, html}
  │
  └─ 6. FileHandlerAgent.create_onedrive_link(output_urls["docx"])
          → onedrive_link: str
```

Agents do **not** call each other directly.

---

## JobState Dataclass

```python
@dataclass
class JobState:
    job_id:     str
    user_id:    str
    file_url:   str
    status:     str       # pending | downloading | formatting | saving | success | partial | failed
    created_at: datetime
    updated_at: datetime
    error:      str | None
```

---

## Input Schema

| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id`  | `str` | UUID for this job |
| `user_id` | `str` | Teams / AAD user ID |
| `file_url`| `str` | Azure Blob SAS URL of the `.docx` file |

---

## Output Schema

```json
{
  "status":           "success | partial | failed",
  "compliance_score": 0.0,
  "formatted_url":    "https://...",
  "diff_url":         "https://...",
  "onedrive_link":    "https://...",
  "summary":          "Formatting complete. 12 change(s). Compliance: 94.5%.",
  "error":            null
}
```

`status = "partial"` when LLM validation timed out and rule-based-only results are returned.

---

## Error Codes

| Code | Trigger |
|------|---------|
| `ERR_CORRUPTED_FILE` | `.docx` could not be downloaded or parsed |
| `ERR_TEMPLATE_NOT_FOUND` | Azure AI Search returned no template rules |
| `ERR_LLM_TIMEOUT` | GPT-4o-mini call timed out (non-fatal — falls back to rule-based) |
| `ERR_STORAGE` | Azure Blob upload or download failure |
| `ERR_FORMATTING` | Unhandled exception in FormattingEngineAgent |

---

## Error Handling Strategy

- **Corrupted file** — caught at download step; returns `failed` immediately.
- **Template not found** — caught at retrieval step; returns `failed`.
- **LLM timeout** — `LLMValidator` returns a fallback dict (`fallback_mode=True`); pipeline continues and returns `partial`.
- **Diff/save errors** — logged and swallowed where safe; `failed` returned for storage errors.
