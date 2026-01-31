"""
DuckDuckGo search client using duckduckgo_search in asyncio.to_thread.
"""
import asyncio
from typing import Any

from src.services.search.search_provider import SearchProvider


class DuckDuckGoClient(SearchProvider):
    """DuckDuckGo search (fallback) via duckduckgo-search."""

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    async def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """Search DDG in a thread; returns list of {title, url, snippet}."""
        try:
            from duckduckgo_search import DDGS
        except ImportError as e:
            raise RuntimeError("duckduckgo-search not installed") from e

        def _run() -> list[dict[str, Any]]:
            with DDGS() as ddgs:
                raw = list(ddgs.text(query, max_results=max_results))
            out: list[dict[str, Any]] = []
            for r in raw:
                out.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", r.get("url", "")),
                    "snippet": r.get("body", r.get("snippet", "")),
                })
            return out

        return await asyncio.wait_for(
            asyncio.to_thread(_run),
            timeout=self.timeout,
        )
