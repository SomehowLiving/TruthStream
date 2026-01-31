"""
Rule-based verdict analysis - no Claude/Groq, uses DDG search results.
"""
from datetime import datetime
from typing import Any

from src.services.search import search_fact_checks, search_news


# Verdict enum matching TruthRegistry.sol
VERDICT_UNVERIFIED = 0
VERDICT_VERIFIED = 1
VERDICT_PARTIALLY_FALSE = 2
VERDICT_OUT_OF_CONTEXT = 3
VERDICT_MANIPULATED = 4

VERDICT_NAMES = {
    VERDICT_UNVERIFIED: "UNVERIFIED",
    VERDICT_VERIFIED: "VERIFIED",
    VERDICT_PARTIALLY_FALSE: "PARTIALLY_FALSE",
    VERDICT_OUT_OF_CONTEXT: "OUT_OF_CONTEXT",
    VERDICT_MANIPULATED: "MANIPULATED",
}


def analyze_investigation(
    content_hash: str,
    text_context: str = "",
    search_query: str | None = None,
) -> dict[str, Any]:
    """
    Rule-based analysis using DuckDuckGo search results.

    Args:
        content_hash: SHA-256 hash of the content
        text_context: Optional text extracted from image/URL
        search_query: Optional custom search query (defaults to text_context)

    Returns:
        Investigation JSON with verdict, sources, confidence, timestamp
    """
    query = search_query or text_context or f"image hash {content_hash[:16]}"
    if not query.strip():
        query = "viral image fact check"

    # Search for fact-checks
    fact_results = search_fact_checks(query, max_results=5)
    news_results = search_news(query, max_results=3)

    # Rule-based verdict logic
    sources = []
    negative_indicators = 0
    positive_indicators = 0

    keywords_false = [
        "fake", "false", "misleading", "manipulated", "deepfake",
        "out of context", "hoax", "debunked", "altered", "doctored",
    ]
    keywords_verified = [
        "verified", "confirmed", "authentic", "real", "accurate",
        "fact-checked", "true", "legitimate",
    ]

    for r in fact_results + news_results:
        snippet = (r.get("snippet") or "").lower()
        title = (r.get("title") or "").lower()
        combined = f"{title} {snippet}"

        sources.append({
            "title": r.get("title", ""),
            "snippet": snippet[:200] + "..." if len(snippet) > 200 else snippet,
            "link": r.get("link", ""),
        })

        for kw in keywords_false:
            if kw in combined:
                negative_indicators += 1
                break
        for kw in keywords_verified:
            if kw in combined:
                positive_indicators += 1
                break

    # Determine verdict and confidence
    total_indicators = negative_indicators + positive_indicators
    if total_indicators == 0:
        verdict = VERDICT_UNVERIFIED
        confidence = 30
        summary = "No fact-check sources found. Unable to verify."
    elif negative_indicators > positive_indicators:
        if negative_indicators >= 3:
            verdict = VERDICT_MANIPULATED
            confidence = min(90, 50 + negative_indicators * 15)
        elif "out of context" in str(sources).lower():
            verdict = VERDICT_OUT_OF_CONTEXT
            confidence = 70
        else:
            verdict = VERDICT_PARTIALLY_FALSE
            confidence = min(85, 50 + negative_indicators * 15)
        summary = f"Found {negative_indicators} source(s) suggesting false or misleading content."
    else:
        verdict = VERDICT_VERIFIED
        confidence = min(95, 60 + positive_indicators * 10)
        summary = f"Found {positive_indicators} source(s) supporting authenticity."

    return {
        "content_hash": content_hash,
        "verdict": verdict,
        "verdict_name": VERDICT_NAMES.get(verdict, "UNVERIFIED"),
        "confidence": min(100, max(0, confidence)),
        "sources": sources[:10],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "summary": summary,
        "search_query": query,
    }
