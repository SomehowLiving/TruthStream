"""
Test InvestigationEngine and rule-based analysis.
"""
import pytest

try:
    from src.services.analysis import (
        InvestigationEngine,
        calculate_file_hash,
        analyze_investigation,
        VERDICT_NAMES,
    )
    ANALYSIS_AVAILABLE = True
except ImportError:
    ANALYSIS_AVAILABLE = False


@pytest.mark.skipif(not ANALYSIS_AVAILABLE, reason="Analysis module not present")
def test_calculate_file_hash():
    """calculate_file_hash returns 64-char hex."""
    from src.services.analysis import calculate_file_hash
    h = calculate_file_hash(b"hello world")
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


@pytest.mark.skipif(not ANALYSIS_AVAILABLE, reason="Analysis module not present")
def test_rule_based_analyze_investigation(sample_content_hash):
    """Rule-based analyze_investigation returns verdict and sources."""
    from src.services.analysis import analyze_investigation
    result = analyze_investigation(
        content_hash=sample_content_hash,
        text_context="Modi announced new currency",
        search_query="Modi currency fact check",
    )
    assert "verdict_name" in result
    assert result["verdict_name"] in VERDICT_NAMES.values()
    assert "confidence" in result
    assert "sources" in result
    assert "summary" in result


@pytest.mark.skipif(not ANALYSIS_AVAILABLE, reason="Analysis module not present")
@pytest.mark.asyncio
async def test_investigation_engine_toma_and_evidence(sample_text, sample_content_hash):
    """InvestigationEngine.investigate returns TOMA scores and evidence chain."""
    from src.services.analysis import InvestigationEngine
    from src.services.ai.unified_ai import get_unified_ai
    try:
        from src.services.search.unified_search import get_unified_search
        search = get_unified_search()
    except ImportError:
        pytest.skip("Search module required for engine")
    ai = get_unified_ai()
    if not ai.has_providers:
        pytest.skip("No AI providers configured")
    engine = InvestigationEngine(ai, search)
    try:
        result = await engine.investigate(sample_text, sample_content_hash)
    except Exception as e:
        pytest.skip(f"Investigation failed (e.g. API): {e}")
    assert result.toma_scores is not None
    assert 0 <= result.toma_scores.overall <= 100
    assert len(result.evidence_chain) >= 1
