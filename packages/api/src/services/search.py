"""
DuckDuckGo search service for fact-checking - free, no API key required.
"""
from typing import Any

from duckduckgo_search import DDGS


def search_fact_checks(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """
    Search DuckDuckGo for fact-check related content.

    Args:
        query: Search query (e.g., "fact check [claim]")
        max_results: Maximum number of results to return

    Returns:
        List of search results with title, snippet, and link
    """
    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    f"fact check {query}",
                    max_results=max_results,
                )
            )
            return [
                {
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "link": r.get("href", ""),
                }
                for r in results
            ]
    except Exception as e:
        return [{"error": str(e), "title": "", "snippet": "", "link": ""}]


def search_news(query: str, max_results: int = 3) -> list[dict[str, Any]]:
    """
    Search DuckDuckGo news for recent coverage.

    Args:
        query: Search query
        max_results: Maximum number of results

    Returns:
        List of news results
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=max_results))
            return [
                {
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "link": r.get("url", ""),
                    "date": r.get("date", ""),
                }
                for r in results
            ]
    except Exception as e:
        return [{"error": str(e), "title": "", "snippet": "", "link": "", "date": ""}]
