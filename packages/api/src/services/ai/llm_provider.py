"""
LLM Provider protocol - base interface for AI analysis providers.
"""
from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Base interface for LLM providers (Anthropic, Groq, etc.)."""

    @abstractmethod
    async def analyze_content(self, text: str) -> dict[str, Any]:
        """Extract claims, sentiment, bias, etc. from text. Return JSON-like dict."""
        ...

    @abstractmethod
    async def synthesize(
        self,
        ai_analysis: dict[str, Any],
        web_results: list[dict[str, Any]],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Synthesize evidence into verdict, confidence, explanation. Return dict."""
        ...
