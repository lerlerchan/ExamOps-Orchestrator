# Result: FormattingEngineAgent

**Status**: Complete
**Date**: 2026-02-26

## Files Created

- `src/agents/formatting_engine/formatting_engine.py`
- `src/agents/formatting_engine/formatting_engine.md`
- `src/agents/formatting_engine/__init__.py`

## Summary

Implemented three classes (two layers + thin wrapper):

### RuleBasedFormatter (Layer 1)
- `process(doc, template_rules) -> Document` — applies all transforms in sequence.
- `_apply_header_footer` — injects/overwrites first-section header and footer text.
- `_standardize_margins` — applies margin_cm from template_rules (defaults: top/bottom 2.5cm, left 3.0cm, right 2.5cm).
- `_fix_numbering` — regex: `Q1)` → `Q1.`, `1a)` → `(a)`.
- `_format_marks` — normalises `[3 marks]`/`(3 Marks)` → `(3 marks)`.
- `_enforce_spacing` — colon whitespace normalisation.
- `_fix_indentation` — sets `left_indent` to `Cm(0)` / `Cm(1.5)` / `Cm(3.0)`.
- `_contains_math` — checks for `m:oMath` XML tag; paragraphs with math are skipped.

### LLMValidator (Layer 2)
- `validate(original, formatted, template_rules) -> dict` — async, calls GPT-4o-mini at `temperature=0.1`.
- On exception returns `{compliance_score: None, fallback_mode: True}` — never raises.

### FormattingEngineAgent (wrapper)
- `process_and_validate(original, template_rules) -> (Document, dict)` — runs L1 then L2.

## Caveats

- `AIProjectClient` import is deferred inside `_call_llm` to avoid import errors without Azure SDK installed.
- `DefaultAzureCredential` is used as primary credential for the Foundry client; `AZURE_FOUNDRY_KEY` is stored but not yet wired (environment-managed identity preferred in production).
- LLM prompt truncates each document to 4000 characters — sufficient for most exam papers; may miss trailing content on very long papers.
