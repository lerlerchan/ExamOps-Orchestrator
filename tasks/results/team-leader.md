# Result: SK "Team Leader" CoordinatorAgent

**Completed**: 2026-02-26
**Status**: Done

## What was done

Replaced the hard-coded sequential call chain in `CoordinatorAgent` with a
Semantic Kernel `ChatCompletionAgent` ("team leader") that instructs pipeline
plugins via automatic function calling.

### New files

| File | Purpose |
|------|---------|
| `src/agents/job_context.py` | `JobContext` dataclass + thread-safe `JobContextRegistry` singleton. Bridges SK string-passing boundary with live Python objects. |
| `src/agents/plugins/__init__.py` | Package init (empty). |
| `src/agents/plugins/file_handler_plugin.py` | `FileHandlerPlugin` — 4 `@kernel_function` methods: `download_document`, `get_template`, `save_outputs`, `create_sharing_link`. |
| `src/agents/plugins/formatting_plugin.py` | `FormattingPlugin` — `format_and_validate` kernel function. |
| `src/agents/plugins/diff_plugin.py` | `DiffPlugin` — `generate_diff` kernel function (synchronous wrapper). |
| `src/agents/kernel_setup.py` | `build_kernel()` — wires `AzureChatCompletion` + 3 plugins into a `Kernel`. |

### Modified files

| File | Change |
|------|--------|
| `src/agents/coordinator_agent/coordinator_agent.py` | `__init__` builds kernel + `ChatCompletionAgent`; `process_job` routes to `_sk_path` first, falls back to `_manual_chain` on any exception. |
| `tests/test_coordinator_agent.py` | Added `TestSKTeamLeaderPath` (4 tests) and `TestSKFallback` (3 tests). |
| `tasks/backend.md` | Appended task definition. |

## Architecture

```
process_job(job_id, user_id, file_url)
    │
    ├─ team_leader is set? ──Yes──► _sk_path()
    │                                    │  registry.create(job_id)
    │                                    │  team_leader.invoke(chat_history)
    │                                    │    └─ SK auto-calls plugins in order:
    │                                    │       1. download_document(job_id)
    │                                    │       2. get_template(job_id)
    │                                    │       3. format_and_validate(job_id)
    │                                    │       4. generate_diff(job_id)
    │                                    │       5. save_outputs(job_id)
    │                                    │       6. create_sharing_link(job_id)
    │                                    │  read ctx from registry
    │                                    │  registry.remove(job_id)
    │                                    └─ return result dict
    │
    └─ No / SK raised ──────────────► _manual_chain()
                                          (original sequential logic, unchanged)
```

## Caveats

- `FunctionChoiceBehavior.Auto()` requires `semantic-kernel>=1.0.0` (already in `requirements.txt`).
- The team leader prompt enforces strict step ordering but the LLM could theoretically skip or reorder steps; the registry will surface missing data as a missing `output_urls` which causes `_sk_path` to raise and trigger the fallback.
- `DiffPlugin.generate_diff` is synchronous because `DiffGeneratorAgent.create_html_diff` is synchronous — SK handles sync kernel functions correctly.
- Azure OpenAI env vars (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_KEY`) must be set for the SK path; if absent, `build_kernel` raises and the coordinator silently falls back to the manual chain.
