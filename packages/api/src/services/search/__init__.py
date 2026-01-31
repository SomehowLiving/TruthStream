"""
Search package: Tavily, DuckDuckGo, unified orchestrator.
"""
from src.services.search.search_provider import SearchProvider
from src.services.search.tavily_client import TavilyClient
from src.services.search.duckduckgo_client import DuckDuckGoClient
from src.services.search.unified_search import UnifiedSearch, get_unified_search

__all__ = [
    "SearchProvider",
    "TavilyClient",
    "DuckDuckGoClient",
    "UnifiedSearch",
    "get_unified_search",
]
