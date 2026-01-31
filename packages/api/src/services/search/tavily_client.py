"""
Tavily search client using httpx.AsyncClient.
"""
from typing import Any

import httpx

from src.config import get_settings
from src.services.search.search_provider import SearchProvider


class TavilyClient(SearchProvider):
    """Tavily search via api.tavily.com."""

    def __init__(self, api_key: str | None = None, timeout: float = 10.0) -> None:
        self.api_key = api_key or get_settings().tavily_api_key
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")

    async def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """Search Tavily; returns list of {title, url, content/snippet}."""
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
        results = data.get("results", [])
        out: list[dict[str, Any]] = []
        for r in results:
            out.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("content", r.get("snippet", "")),
            })
        return out
