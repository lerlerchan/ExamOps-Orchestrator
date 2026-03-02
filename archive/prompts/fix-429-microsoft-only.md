# Fix: Azure OpenAI 429 Rate Limit — Microsoft-Only Solutions

## Problem
Azure OpenAI S0 student subscription hitting 429 RateLimitReached. Cannot increase quota on student plan.

## Solution Priority (all Microsoft ecosystem — hackathon safe)

---

### Option A: GitHub Models (RECOMMENDED — Free, Microsoft-owned)

GitHub Models is a **Microsoft product** (GitHub is owned by Microsoft). It provides free API access to GPT-4o-mini, Phi-4, and other models. Uses the **same OpenAI SDK** — minimal code change.

**Rate limits (free tier):**
- GPT-4o-mini: 150 requests/day, 15 req/min, 8000 tokens in / 4000 out
- Phi-4: 150 requests/day, 15 req/min, 8000 tokens in / 4000 out

**Setup:**
1. Go to https://github.com/settings/tokens → Generate new token (classic)
2. Grant `models:read` permission only
3. Add to `.env`: `GITHUB_TOKEN=ghp_xxxxxxxxxxxx`

**Code — drop-in replacement using same OpenAI SDK:**
```python
from openai import AsyncOpenAI

# GitHub Models client (OpenAI-compatible endpoint)
github_client = AsyncOpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.getenv("GITHUB_TOKEN")
)

# Use exactly like Azure OpenAI
response = await github_client.chat.completions.create(
    model="gpt-4o-mini",  # or "Phi-4" or "Phi-4-mini-instruct"
    messages=messages,
    temperature=0.1,
    max_tokens=2000
)
```

---

### Option B: Deploy Phi-4 via Azure AI Foundry (Serverless API — Pay-as-you-go)

Microsoft's own open model. Deploy as serverless API in Foundry — separate quota from your OpenAI S0 limit.

**NOTE:** Student subscriptions MAY block this. Try it — if deployment fails, use Option A.

1. Go to https://ai.azure.com → Model Catalog → Search "Phi-4"
2. Click "Deploy" → Serverless API
3. Copy endpoint + key

```python
phi_client = AsyncOpenAI(
    base_url="https://<your-phi4-endpoint>.models.ai.azure.com/v1",
    api_key=os.getenv("AZURE_PHI4_KEY")
)

response = await phi_client.chat.completions.create(
    model="Phi-4",
    messages=messages,
    temperature=0.1
)
```

---

### Option C: Reduce token usage to stay within S0 limits

If you want to keep using Azure OpenAI only:
- **Chunk the syllabus** — don't send full doc in one call. Split into pages, extract CLOs per chunk, merge results
- **Use shorter system prompts** — trim the validation prompt (currently very long in PRD.md)
- **Cache results** — store extracted CLOs in session, don't re-extract on every call
- **Add 60s retry backoff** — most 429s resolve after waiting

---

## Implementation: Unified LLM Client with Fallback

Create `src/utils/llm_client.py`:

```python
import os
from openai import AsyncOpenAI, AsyncAzureOpenAI, RateLimitError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

class LLMClient:
    """Unified LLM client: Azure OpenAI → GitHub Models fallback.
    All Microsoft ecosystem. Same OpenAI SDK."""

    def __init__(self):
        # Primary: Azure OpenAI (existing deployment)
        self.primary = AsyncAzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-01"
        )
        self.primary_model = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

        # Fallback: GitHub Models (free, same OpenAI API format)
        gh_token = os.getenv("GITHUB_TOKEN")
        self.fallback = AsyncOpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=gh_token
        ) if gh_token else None
        self.fallback_model = "gpt-4o-mini"  # or "Phi-4-mini-instruct"

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=30, min=60, max=180),
        stop=stop_after_attempt(2),
    )
    async def _call_primary(self, messages, temperature=0.1, max_tokens=2000):
        response = await self.primary.chat.completions.create(
            model=self.primary_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    async def chat(self, messages, temperature=0.1, max_tokens=2000):
        """Try Azure OpenAI first, fall back to GitHub Models on 429."""
        try:
            return await self._call_primary(messages, temperature, max_tokens)
        except RateLimitError:
            if not self.fallback:
                raise
            print("[LLMClient] Azure rate limited → switching to GitHub Models")
            response = await self.fallback.chat.completions.create(
                model=self.fallback_model,
                messages=messages,
                temperature=temperature,
                max_tokens=min(max_tokens, 4000)  # GitHub Models cap
            )
            return response.choices[0].message.content
```

## Refactor All Agents

Replace direct Azure OpenAI calls in ALL agents with `LLMClient`:

```python
# In every agent file:
from src.utils.llm_client import LLMClient

class SyllabusAgent:
    def __init__(self):
        self.llm = LLMClient()

    async def extract_clo_plo(self, doc_text: str) -> dict:
        result = await self.llm.chat(messages=[
            {"role": "system", "content": "Extract CLOs and PLOs..."},
            {"role": "user", "content": doc_text}
        ])
        return json.loads(result)
```

Do the same for: `FormattingEngineAgent` (LLMValidator), `QuestionCopilotAgent`, `ModerationFormAgent`.

## Frontend Fix: Stop Infinite Spinner

In `src/web/index.html`, the upload-syllabus fetch call must handle errors:

```javascript
try {
    const response = await fetch('/api/upload-syllabus', { ... });
    if (!response.ok) {
        const error = await response.json();
        showError(`CLO/PLO extraction failed: ${error.message || 'Unknown error'}`);
        return;
    }
    // success path...
} catch (err) {
    showError('Network error. Please try again.');
}
```

## .env additions
```
# GitHub Models (free fallback)
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

## Test
After implementing, retry the syllabus upload. If Azure 429 hits, it should silently fall back to GitHub Models and complete within ~10 seconds.
