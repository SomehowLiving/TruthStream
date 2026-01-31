"""
Test AI providers (UnifiedAI, Anthropic, Groq fallback).
"""
import pytest

from src.config import get_settings


@pytest.fixture
def has_ai_key():
    settings = get_settings()
    return bool(settings.anthropic_api_key or settings.groq_api_key)


@pytest.mark.asyncio
async def test_unified_ai_analyze(sample_text, has_ai_key):
    """Test UnifiedAI.analyze_with_fallback returns dict with claims or error."""
    from src.services.ai.unified_ai import UnifiedAI

    ai = UnifiedAI()
    result = await ai.analyze_with_fallback(sample_text)
    assert isinstance(result, dict)
    if result.get("error"):
        if not has_ai_key:
            pytest.skip("No AI keys configured; response is expected error dict")
        assert "message" in result
        return
    assert "provider" in result
    assert result["provider"] in ("anthropic", "groq")
    assert "claims" in result
    assert isinstance(result["claims"], list)


@pytest.mark.asyncio
async def test_unified_ai_synthesize_returns_verdict(has_ai_key):
    """Test synthesize_with_fallback returns verdict and confidence."""
    from src.services.ai.unified_ai import UnifiedAI

    ai = UnifiedAI()
    ai_result = {"claims": ["Earth is flat"], "summary": "Test", "provider": "test"}
    web_results = [{"claim": "Earth is flat", "verification": {"answer": "False", "provider": "ddg"}}]
    result = await ai.synthesize_with_fallback(ai_result, web_results, {})
    assert isinstance(result, dict)
    assert "verdict" in result
    assert "confidence" in result
    if result.get("error") and not has_ai_key:
        pytest.skip("No AI keys; synthesis returned error dict")
    assert result["verdict"] in (
        "verified",
        "partially_false",
        "out_of_context",
        "manipulated",
        "unverified",
    )
    assert 0 <= result["confidence"] <= 1.0


def test_get_unified_ai_singleton():
    """get_unified_ai returns same instance."""
    from src.services.ai.unified_ai import get_unified_ai, UnifiedAI

    a = get_unified_ai()
    b = get_unified_ai()
    assert a is b
    assert isinstance(a, UnifiedAI)
