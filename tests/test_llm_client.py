"""
Unit tests for src/utils/llm_client.py

Covers:
- Azure OpenAI success path
- Azure 429 → GitHub Models fallback
- No GITHUB_TOKEN → re-raises RateLimitError
- Streaming fallback on 429
"""

import sys
import types
import pytest
from unittest.mock import AsyncMock, MagicMock


# ---------------------------------------------------------------------------
# Module-level openai stub so LLMClient.__init__ can import AsyncAzureOpenAI
# ---------------------------------------------------------------------------

def _install_openai_stub():
    """
    Install a minimal openai stub into sys.modules so that LLMClient can be
    imported and instantiated in environments where openai>=1.0 is not present.
    The real AsyncAzureOpenAI / AsyncOpenAI are replaced with MagicMock classes.
    """
    stub = types.ModuleType("openai")
    stub.AsyncAzureOpenAI = MagicMock
    stub.AsyncOpenAI = MagicMock

    class _RateLimitError(Exception):
        def __init__(self, message="", response=None, body=None):
            super().__init__(message)
            self.response = response
            self.body = body

    stub.RateLimitError = _RateLimitError
    sys.modules["openai"] = stub
    return stub


_openai_stub = _install_openai_stub()
RateLimitError = _openai_stub.RateLimitError  # re-export for test use


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _env_vars(monkeypatch):
    """Provide required env vars for LLMClient construction."""
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://fake.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_KEY", "fake-key")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    monkeypatch.setenv("GITHUB_TOKEN", "fake-gh-token")


@pytest.fixture()
def client():
    """A fresh LLMClient instance per test."""
    from src.utils.llm_client import LLMClient
    return LLMClient()


# ---------------------------------------------------------------------------
# Test: Azure success path
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chat_azure_success(client):
    """chat() returns the Azure response when Azure succeeds."""
    client._azure_chat = AsyncMock(return_value="Hello from Azure")

    result = await client.chat(messages=[{"role": "user", "content": "hi"}])

    client._azure_chat.assert_awaited_once()
    assert result == "Hello from Azure"


# ---------------------------------------------------------------------------
# Test: Azure 429 → fallback to GitHub Models
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chat_falls_back_on_rate_limit(client):
    """chat() uses GitHub Models when Azure returns 429 RateLimitError."""
    client._azure_chat = AsyncMock(side_effect=RateLimitError("rate limited"))
    client._github_chat = AsyncMock(return_value="Hello from GitHub Models")
    # Ensure _fallback is not None so the branch is taken
    client._fallback = MagicMock()

    result = await client.chat(messages=[{"role": "user", "content": "hi"}])

    client._azure_chat.assert_awaited_once()
    client._github_chat.assert_awaited_once()
    assert result == "Hello from GitHub Models"


# ---------------------------------------------------------------------------
# Test: No GITHUB_TOKEN → re-raises RateLimitError
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chat_no_token_reraises(client):
    """chat() re-raises RateLimitError when no fallback is configured."""
    client._azure_chat = AsyncMock(side_effect=RateLimitError("rate limited"))
    client._fallback = None  # simulates no GITHUB_TOKEN

    with pytest.raises(RateLimitError):
        await client.chat(messages=[{"role": "user", "content": "hi"}])


# ---------------------------------------------------------------------------
# Test: Streaming fallback on 429
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_stream_falls_back_on_rate_limit(client):
    """stream() switches to GitHub Models generator on Azure 429."""
    client._fallback = MagicMock()

    async def _azure_raises(*args, **kwargs):
        raise RateLimitError("rate limited")
        yield  # make it an async generator

    async def _github_gen(*args, **kwargs):
        for tok in ["chunk1", "chunk2"]:
            yield tok

    client._azure_stream = _azure_raises
    client._github_stream = _github_gen

    tokens = []
    async for tok in client.stream(messages=[{"role": "user", "content": "hi"}]):
        tokens.append(tok)

    assert tokens == ["chunk1", "chunk2"]
