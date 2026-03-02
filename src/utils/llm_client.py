"""
LLMClient — Unified LLM client with multi-backend primary + GitHub Models fallback.

Selects the primary backend via the LLM_BACKEND env var:
  "foundry" (default) — Azure AI Foundry → Phi-3.5-mini-instruct
  "ollama"            — Ollama → Phi-4 (fully offline, OpenAI-compatible API)
  "azure"             — Azure OpenAI → GPT-4o-mini (legacy)

GitHub Models stays as a last-resort 429 fallback for all backends.

Environment variables:
    LLM_BACKEND                — "foundry" | "ollama" | "azure" (default: foundry)

    # Foundry backend (default):
    AZURE_FOUNDRY_ENDPOINT     — Azure AI Foundry endpoint
    AZURE_FOUNDRY_KEY          — Azure AI Foundry key
    AZURE_FOUNDRY_DEPLOYMENT   — model deployment name (default: Phi-3.5-mini-instruct)

    # Ollama backend:
    OLLAMA_BASE_URL            — Ollama OpenAI-compat base URL (default: http://localhost:11434/v1)
    OLLAMA_MODEL               — Ollama model tag (default: phi4)

    # Azure backend (legacy):
    AZURE_OPENAI_ENDPOINT      — Azure OpenAI endpoint
    AZURE_OPENAI_KEY           — Azure OpenAI key
    AZURE_OPENAI_DEPLOYMENT    — deployment name (default: gpt-4o-mini)

    # Fallback (all backends):
    GITHUB_TOKEN               — GitHub personal access token (fallback on 429)
                                 Grant models:read permission.
                                 https://github.com/settings/tokens

Rate limits (GitHub Models free tier):
    GPT-4o-mini : 150 req/day, 15 req/min, 8000 tokens in / 4000 out
    Phi-4       : 150 req/day, 15 req/min, 8000 tokens in / 4000 out
"""

import logging
import os

logger = logging.getLogger(__name__)

_GITHUB_MODELS_BASE_URL = "https://models.inference.ai.azure.com"
_GITHUB_FALLBACK_MODEL = "gpt-4o-mini"
_GITHUB_MAX_TOKENS = 4000  # GitHub Models output cap


class LLMClient:
    """
    Unified LLM client: configurable primary backend → GitHub Models fallback.

    Usage (non-streaming)::

        client = LLMClient()
        text = await client.chat(messages=[{"role": "user", "content": "Hello"}])

    Usage (streaming)::

        async for chunk in client.stream(messages):
            yield chunk
    """

    def __init__(self) -> None:
        from openai import AsyncAzureOpenAI, AsyncOpenAI

        backend = os.getenv("LLM_BACKEND", "foundry").lower()

        if backend == "ollama":
            self._primary = AsyncOpenAI(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                api_key="ollama",   # SDK requires non-empty; Ollama ignores it
            )
            self._primary_model = os.getenv("OLLAMA_MODEL", "phi4")

        elif backend == "foundry":
            self._primary = AsyncAzureOpenAI(
                azure_endpoint=os.getenv("AZURE_FOUNDRY_ENDPOINT", ""),
                api_key=os.getenv("AZURE_FOUNDRY_KEY", ""),
                api_version="2024-02-01",
            )
            self._primary_model = os.getenv(
                "AZURE_FOUNDRY_DEPLOYMENT", "Phi-3.5-mini-instruct"
            )

        else:  # "azure" — original behaviour
            self._primary = AsyncAzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
                api_key=os.getenv("AZURE_OPENAI_KEY", ""),
                api_version="2024-02-01",
            )
            self._primary_model = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

        gh_token = os.getenv("GITHUB_TOKEN")
        self._fallback = (
            AsyncOpenAI(
                base_url=_GITHUB_MODELS_BASE_URL,
                api_key=gh_token,
            )
            if gh_token
            else None
        )

    async def chat(
        self,
        messages: list,
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> str:
        """
        Non-streaming completion. Tries the primary backend first, falls back to
        GitHub Models on 429 RateLimitError.

        Returns:
            Assistant message content string.

        Raises:
            openai.RateLimitError: if both primary and GitHub Models are unavailable.
        """
        from openai import RateLimitError

        try:
            return await self._primary_chat(messages, temperature, max_tokens)
        except RateLimitError:
            if self._fallback is None:
                logger.error(
                    "Primary LLM 429 and no GITHUB_TOKEN fallback configured"
                )
                raise
            logger.warning(
                "Primary LLM rate limited (429) → falling back to GitHub Models"
            )
            return await self._github_chat(messages, temperature, max_tokens)

    async def stream(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        """
        Streaming completion. Yields token strings.
        Falls back to GitHub Models on 429.

        Usage::

            async for token in client.stream(messages):
                print(token, end="")
        """
        from openai import RateLimitError

        try:
            async for token in self._primary_stream(messages, temperature, max_tokens):
                yield token
        except RateLimitError:
            if self._fallback is None:
                logger.error(
                    "Primary LLM 429 and no GITHUB_TOKEN fallback configured"
                )
                raise
            logger.warning(
                "Primary LLM rate limited (429) during streaming → "
                "falling back to GitHub Models"
            )
            async for token in self._github_stream(messages, temperature, max_tokens):
                yield token

    # ── Primary backend ───────────────────────────────────────────────────────

    async def _primary_chat(self, messages, temperature, max_tokens) -> str:
        response = await self._primary.chat.completions.create(
            model=self._primary_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    async def _primary_stream(self, messages, temperature, max_tokens):
        stream = await self._primary.chat.completions.create(
            model=self._primary_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    # ── GitHub Models fallback ────────────────────────────────────────────────

    async def _github_chat(self, messages, temperature, max_tokens) -> str:
        capped = min(max_tokens, _GITHUB_MAX_TOKENS)
        response = await self._fallback.chat.completions.create(
            model=_GITHUB_FALLBACK_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=capped,
        )
        return response.choices[0].message.content

    async def _github_stream(self, messages, temperature, max_tokens):
        capped = min(max_tokens, _GITHUB_MAX_TOKENS)
        stream = await self._fallback.chat.completions.create(
            model=_GITHUB_FALLBACK_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=capped,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
