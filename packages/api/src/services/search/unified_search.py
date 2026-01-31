"""
Unified search: Tavily (primary) → DuckDuckGo (fallback).
"""
from typing import Any

from src.services.search.duckduckgo_client import DuckDuckGoClient
from src.services.search.tavily_client import TavilyClient
from src.services.search.search_provider import SearchProvider


class UnifiedSearch:
    """Orchestrates search with Tavily first, DDG fallback."""

    def __init__(self) -> None:
        self._primary: SearchProvider | None = None
        self._fallback: SearchProvider | None = None
        try:
            self._primary = TavilyClient()
        except (ValueError, Exception):
            pass
        try:
            self._fallback = DuckDuckGoClient()
        except Exception:
            pass

    @property
    def has_providers(self) -> bool:
        return self._primary is not None or self._fallback is not None

    async def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """Try primary (Tavily), then fallback (DDG)."""
        for provider in (self._primary, self._fallback):
            if provider is None:
                continue
            try:
                return await provider.search(query, max_results=max_results)
            except Exception:
                continue
        return []


_unified_search: UnifiedSearch | None = None


def get_unified_search() -> UnifiedSearch:
    """Singleton factory for UnifiedSearch."""
    global _unified_search
    if _unified_search is None:
        _unified_search = UnifiedSearch()
    return _unified_search
