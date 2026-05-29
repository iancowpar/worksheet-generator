"""Provider boundary for Round Two's AI calls.

The worksheet pipeline should not care whether extraction/generation is backed
by Claude today, Gemini later, or a district-hosted gateway in between. This
module owns the provider-specific message shapes and environment variables;
`problem_generator.py` owns prompt assembly, JSON parsing, verification, and
retry behavior.
"""

from __future__ import annotations

import base64
import os
from functools import lru_cache
from typing import Protocol

from anthropic import Anthropic


class MissingAPIKey(RuntimeError):
    """The selected AI provider is missing its required API key."""


class UnsupportedLLMProvider(RuntimeError):
    """ROUND_TWO_LLM_PROVIDER names a provider this build does not implement."""


class LLMProvider(Protocol):
    """Minimal text/PDF interface Round Two needs from an AI backend."""

    def extract_problem_types(self, pdf_bytes: bytes, system: str, user: str) -> str:
        """Return the raw JSON-ish extraction response for one uploaded PDF."""
        ...

    def generate_problem(self, system: str, user: str) -> str:
        """Return the raw JSON-ish response for one generated problem."""
        ...

    def verify_word_problem(self, system: str, user: str) -> str:
        """Return the raw JSON-ish response for a solve-from-scratch check."""
        ...


class AnthropicProvider:
    """Anthropic Messages API implementation.

    Model names are configurable so schools can pin approved models or route
    through an Anthropic-compatible gateway without changing app code.
    """

    def __init__(self) -> None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise MissingAPIKey(
                "ANTHROPIC_API_KEY is not set. For local dev, export it; for "
                "Streamlit Community Cloud, paste it into the app's Secrets UI. "
                "See .streamlit/secrets.toml.example on the publish-prep branch."
            )
        self._client = Anthropic(api_key=api_key)
        self.extract_model = os.environ.get("ROUND_TWO_EXTRACT_MODEL", "claude-opus-4-7")
        self.generate_model = os.environ.get("ROUND_TWO_GENERATE_MODEL", "claude-sonnet-4-6")
        self.verify_model = os.environ.get("ROUND_TWO_VERIFY_MODEL", self.generate_model)
        self.extract_max_tokens = int(os.environ.get("ROUND_TWO_EXTRACT_MAX_TOKENS", "8192"))
        self.generate_max_tokens = int(os.environ.get("ROUND_TWO_GENERATE_MAX_TOKENS", "2048"))
        self.verify_max_tokens = int(os.environ.get("ROUND_TWO_VERIFY_MAX_TOKENS", "1024"))

    def extract_problem_types(self, pdf_bytes: bytes, system: str, user: str) -> str:
        pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("ascii")
        response = self._client.messages.create(
            model=self.extract_model,
            max_tokens=self.extract_max_tokens,
            system=system,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_b64,
                        },
                    },
                    {"type": "text", "text": user},
                ],
            }],
        )
        return _anthropic_response_text(response)

    def generate_problem(self, system: str, user: str) -> str:
        return self._text_call(self.generate_model, self.generate_max_tokens, system, user)

    def verify_word_problem(self, system: str, user: str) -> str:
        return self._text_call(self.verify_model, self.verify_max_tokens, system, user)

    def _text_call(self, model: str, max_tokens: int, system: str, user: str) -> str:
        response = self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return _anthropic_response_text(response)


def _anthropic_response_text(response) -> str:
    """Concatenate text blocks from a Messages API response."""
    parts = []
    for block in response.content:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "".join(parts)


@lru_cache(maxsize=1)
def get_llm_provider() -> LLMProvider:
    """Build the configured provider once per process.

    `anthropic` remains the default to preserve current behavior. `gemini` is
    intentionally explicit rather than silently falling back, because a school
    deployment should fail loudly if its approved backend is not wired yet.
    """
    provider = os.environ.get("ROUND_TWO_LLM_PROVIDER", "anthropic").strip().lower()
    if provider in ("anthropic", "claude"):
        return AnthropicProvider()
    if provider == "gemini":
        raise UnsupportedLLMProvider(
            "ROUND_TWO_LLM_PROVIDER=gemini is reserved for the district Gemini "
            "backend, but this build only implements the provider boundary. "
            "Add a GeminiProvider before enabling it in production."
        )
    raise UnsupportedLLMProvider(f"Unsupported ROUND_TWO_LLM_PROVIDER: {provider}")
