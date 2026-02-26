# FileHandlerAgent

**File**: `src/agents/file_handler_agent/file_handler_agent.py`

---

## Purpose

Handles all file I/O for the ExamOps pipeline: Azure Blob Storage CRUD across three containers, vector similarity retrieval of template rules from Azure AI Search, and OneDrive shareable link creation via Microsoft Graph API.

---

## Azure Blob Containers

| Container | Purpose |
|-----------|---------|
| `examops-input` | Incoming `.docx` files uploaded by users |
| `examops-output` | Formatted `.docx` files + HTML diff reports |
| `examops-templates` | Static template reference files (read-only) |

---

## Method Signatures

### `upload_to_blob`

```python
async def upload_to_blob(
    file_stream: io.BytesIO,
    filename: str,
    user_id: str,
) -> str
```

Uploads a `.docx` to `examops-input`. Blob name: `{timestamp}_{user_id}_{filename}`.
Returns a **1-hour SAS URL**.

---

### `download_from_blob`

```python
async def download_from_blob(blob_url: str) -> Document
```

Downloads the blob at `blob_url` and returns a `python-docx` `Document`.
Raises `ValueError` if the content cannot be parsed as `.docx`.

---

### `get_template_from_vectordb`

```python
async def get_template_from_vectordb(query: str) -> dict
```

1. Generates an `text-embedding-ada-002` embedding for `query`.
2. Runs a k-NN vector search against the `exam-templates` Azure AI Search index.
3. Returns the top result's `template_rules` field as a dict.

Raises `RuntimeError` if no results are found.

---

### `save_outputs`

```python
async def save_outputs(
    formatted_doc: Document,
    diff_html: str,
    job_id: str,
) -> dict
```

Saves formatted `.docx` and HTML diff to `examops-output`.
Returns `{"docx": "<sas_url>", "html": "<sas_url>"}` — both with **1-hour expiry**.

---

### `create_onedrive_link`

```python
async def create_onedrive_link(blob_url: str) -> str
```

Uploads the file from `blob_url` to the user's OneDrive via Graph API, then creates an anonymous view-only sharing link.
Returns the shareable URL string.

---

## Environment Variables

| Variable | Used By |
|----------|---------|
| `AZURE_STORAGE_CONNECTION_STRING` | All blob operations |
| `AZURE_SEARCH_ENDPOINT` | `get_template_from_vectordb` |
| `AZURE_SEARCH_KEY` | `get_template_from_vectordb` |
| `AZURE_OPENAI_ENDPOINT` | Ada-002 embedding generation |
| `AZURE_OPENAI_KEY` | Ada-002 embedding generation |
| `GRAPH_TENANT_ID` | Graph API token acquisition |
| `GRAPH_CLIENT_ID` | Graph API token acquisition |
| `GRAPH_CLIENT_SECRET` | Graph API token acquisition |

All variables are read via `os.getenv()` at init time. No import-time errors if they are absent — errors surface at runtime when the relevant method is called.

---

## SAS Token Expiry Policy

- Input uploads: **1 hour** — sufficient for the pipeline to complete.
- Output files: **1 hour** — refreshed on demand by calling `save_outputs` again.
- OneDrive links: **anonymous view** — no expiry (managed by SharePoint/OneDrive settings).

---

## Azure AI Search Index Schema (expected)

The `exam-templates` index must have:

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Edm.String` | Key field |
| `template_rules` | `Edm.ComplexType` / JSON | Formatting rules dict |
| `content_vector` | `Collection(Edm.Single)` | Ada-002 embedding (1536 dims) |
