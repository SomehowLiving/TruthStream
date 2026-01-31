"""
Test search providers (Tavily, DuckDuckGo fallback).
"""
import pytest

try:
    from src.services.search.unified_search import UnifiedSearch, get_unified_search
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False


@pytest.mark.skipif(not SEARCH_AVAILABLE, reason="Search module not present")
@pytest.mark.asyncio
async def test_unified_search_returns_sources():
    """Test UnifiedSearch.search returns answer and sources list."""
    search = UnifiedSearch()
    result = await search.search("Modi currency fact check", max_results=3)
    assert isinstance(result, dict)
    assert "sources" in result
    assert isinstance(result["sources"], list)
    assert "provider" in result
    assert result["provider"] in ("tavily", "duckduckgo")


@pytest.mark.skipif(not SEARCH_AVAILABLE, reason="Search module not present")
@pytest.mark.asyncio
async def test_fact_check_claims_returns_list():
    """Test fact_check_claims returns list of {claim, verification}."""
    search = UnifiedSearch()
    result = await search.fact_check_claims(["Modi announced new currency"])
    assert isinstance(result, list)
    for item in result:
        assert "claim" in item
        assert "verification" in item


@pytest.mark.skipif(not SEARCH_AVAILABLE, reason="Search module not present")
def test_get_unified_search_singleton():
    """get_unified_search returns same instance."""
    a = get_unified_search()
    b = get_unified_search()
    assert a is b
