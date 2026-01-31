"""
Abstract base class for search providers (Tavily, DuckDuckGo, etc.).
"""
from abc import ABC, abstractmethod
from typing import Any


class SearchProvider(ABC):
    """Base interface for search providers."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """
        Run a search query. Returns list of dicts with at least:
        title, url, snippet (or body).
        """
        ...
