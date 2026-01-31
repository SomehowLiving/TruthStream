"""
Unified AI with Anthropic → Groq fallback.
"""
import asyncio
from typing import Any

from src.config import get_settings
from src.services.ai.anthropic_client import AnthropicClient
from src.services.ai.groq_client import GroqClient
from src.services.ai.llm_provider import LLMProvider


def _get_providers() -> list[LLMProvider]:
    """Build list of available providers (Anthropic first, then Groq)."""
    providers: list[LLMProvider] = []
    settings = get_settings()
    if settings.anthropic_api_key:
        try:
            providers.append(AnthropicClient())
        except ValueError:
            pass
    if settings.groq_api_key:
        try:
            providers.append(GroqClient())
        except ValueError:
            pass
    return providers


class UnifiedAI:
    """Unified AI with automatic Anthropic → Groq fallback."""

    def __init__(self) -> None:
        self._providers = _get_providers()

    @property
    def has_providers(self) -> bool:
        """Whether any AI provider is configured."""
        return len(self._providers) > 0

    async def analyze_with_fallback(
        self,
        text: str,
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        """
        Try Anthropic first, fall back to Groq on exception or timeout.

        Returns:
            Dict with provider, claims, sentiment, etc.
            On failure: {"error": True, "message": "All AI providers failed"}
        """
        if not self._providers:
            return {
                "error": True,
                "message": "All AI providers failed",
                "provider": None,
                "claims": [],
            }

        last_error: Exception | None = None
        for provider in self._providers:
            try:
                result = await asyncio.wait_for(
                    provider.analyze_content(text),
                    timeout=timeout,
                )
                if "error" in result and result.get("error"):
                    continue
                return result
            except asyncio.TimeoutError as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                continue

        return {
            "error": True,
            "message": "All AI providers failed",
            "provider": None,
            "claims": [],
            "detail": str(last_error) if last_error else None,
        }

    async def synthesize_with_fallback(
        self,
        ai_analysis: dict[str, Any],
        web_results: list[dict[str, Any]],
        metadata: dict[str, Any],
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        """
        Try Anthropic first, fall back to Groq on exception or timeout.

        Returns:
            Dict with verdict, confidence, explanation, toma_transparency, toma_alignment.
            On failure: {"error": True, "message": "All AI providers failed", ...}
        """
        if not self._providers:
            return {
                "error": True,
                "message": "All AI providers failed",
                "verdict": "unverified",
                "confidence": 0.0,
                "explanation": "No AI providers configured",
                "toma_transparency": 50,
                "toma_alignment": 50,
            }

        last_error: Exception | None = None
        for provider in self._providers:
            try:
                result = await asyncio.wait_for(
                    provider.synthesize(ai_analysis, web_results, metadata),
                    timeout=timeout,
                )
                if "error" in result and result.get("error"):
                    continue
                return result
            except asyncio.TimeoutError as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                continue

        return {
            "error": True,
            "message": "All AI providers failed",
            "verdict": "unverified",
            "confidence": 0.0,
            "explanation": str(last_error) if last_error else "Synthesis failed",
            "toma_transparency": 50,
            "toma_alignment": 50,
            "detail": str(last_error) if last_error else None,
        }


_unified_ai: "UnifiedAI | None" = None


def get_unified_ai() -> "UnifiedAI":
    """Singleton factory for UnifiedAI."""
    global _unified_ai
    if _unified_ai is None:
        _unified_ai = UnifiedAI()
    return _unified_ai
