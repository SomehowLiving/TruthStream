"""
Investigation engine: hash, AI + search orchestration, TOMA scores, evidence chain.
"""
import hashlib
from datetime import datetime, timezone
from typing import Any

from src.models import (
    InvestigationResult,
    SourceEvidence,
    TOMAScores,
    VerdictCategory,
)
from src.services.ai.llm_provider import LLMProvider
from src.services.search.search_provider import SearchProvider


VERDICT_NAMES = {
    "verified": "verified",
    "partially_false": "partially_false",
    "out_of_context": "out_of_context",
    "manipulated": "manipulated",
    "unverified": "unverified",
}


def calculate_file_hash(file_bytes: bytes) -> str:
    """SHA-256 hash of file bytes; returns 64-char hex string (no 0x prefix)."""
    return hashlib.sha256(file_bytes).hexdigest()


def analyze_investigation(
    content_hash: str,
    text_context: str,
    search_query: str,
) -> dict[str, Any]:
    """
    Rule-based analysis when AI/search unavailable.
    Returns dict with verdict_name, confidence, sources, summary.
    """
    verdict_name = VERDICT_NAMES["unverified"]
    confidence = 0.0
    sources: list[dict[str, Any]] = []
    summary = "Rule-based fallback: no AI or search available."
    return {
        "verdict_name": verdict_name,
        "confidence": confidence,
        "sources": sources,
        "summary": summary,
    }


def _verdict_str_to_enum(s: str) -> VerdictCategory:
    """Map synthesis verdict string to VerdictCategory."""
    m = {
        "verified": VerdictCategory.VERIFIED,
        "partially_false": VerdictCategory.PARTIALLY_FALSE,
        "out_of_context": VerdictCategory.OUT_OF_CONTEXT,
        "manipulated": VerdictCategory.MANIPULATED,
        "unverified": VerdictCategory.UNVERIFIED,
    }
    key = (s or "").strip().lower().replace(" ", "_")
    return m.get(key, VerdictCategory.UNVERIFIED)


def _build_toma(
    transparency: int | None,
    alignment: int | None,
) -> TOMAScores:
    """Build TOMAScores from synthesis toma_transparency and toma_alignment."""
    t = max(0, min(100, transparency if transparency is not None else 50))
    a = max(0, min(100, alignment if alignment is not None else 50))
    ownership = (t + a) // 2
    overall = (t + ownership + a) // 3
    return TOMAScores(transparency=t, ownership=ownership, alignment=a, overall=overall)


class InvestigationEngine:
    """Orchestrates AI analysis, search, synthesis; builds InvestigationResult."""

    def __init__(self, ai: LLMProvider, search: SearchProvider | None) -> None:
        self._ai = ai
        self._search = search

    async def investigate(
        self,
        text_content: str,
        content_hash: str,
        timeout: float = 10.0,
    ) -> InvestigationResult:
        """
        Run AI analysis, optional search, synthesis; compute TOMA and evidence chain.
        Returns InvestigationResult (da_blob_id and tx_hash left None; set by API).
        """
        now = datetime.now(timezone.utc)
        evidence_chain: list[SourceEvidence] = []
        ai_provider = "none"
        verdict = VerdictCategory.UNVERIFIED
        confidence = 0.0
        summary = "Investigation failed."
        toma_scores = TOMAScores(transparency=50, ownership=50, alignment=50, overall=50)

        # 1. AI analysis
        if hasattr(self._ai, "analyze_with_fallback"):
            ai_result = await self._ai.analyze_with_fallback(text_content, timeout=timeout)
        else:
            ai_result = await self._ai.analyze_content(text_content)

        if ai_result.get("error"):
            return InvestigationResult(
                content_hash=content_hash,
                timestamp=now,
                verdict=verdict,
                confidence=0.0,
                toma_scores=toma_scores,
                summary=ai_result.get("message", summary),
                evidence_chain=[
                    SourceEvidence(
                        type="ai_analysis",
                        source=ai_result.get("provider", "none"),
                        query=None,
                        result_summary="AI analysis failed",
                        timestamp=now,
                        url=None,
                    )
                ],
                ai_model=ai_result.get("provider", "none"),
                da_blob_id=None,
                tx_hash=None,
            )

        ai_provider = ai_result.get("provider", "unknown")
        evidence_chain.append(
            SourceEvidence(
                type="ai_analysis",
                source=ai_provider,
                query=None,
                result_summary=ai_result.get("summary", "")[:500],
                timestamp=now,
                url=None,
            )
        )

        # 2. Web search (if available)
        web_results: list[dict[str, Any]] = []
        query = text_content[:100].strip() or "fact check"
        if self._search and hasattr(self._search, "search"):
            try:
                web_results = await self._search.search(query, max_results=5)
                for r in web_results:
                    evidence_chain.append(
                        SourceEvidence(
                            type="web_search",
                            source=r.get("title", "web"),
                            query=query,
                            result_summary=(r.get("snippet", "") or r.get("body", ""))[:300],
                            timestamp=now,
                            url=r.get("url"),
                        )
                    )
            except Exception:
                evidence_chain.append(
                    SourceEvidence(
                        type="web_search",
                        source="fallback",
                        query=query,
                        result_summary="Search failed or unavailable",
                        timestamp=now,
                        url=None,
                    )
                )

        if not evidence_chain:
            evidence_chain.append(
                SourceEvidence(
                    type="placeholder",
                    source="none",
                    query=None,
                    result_summary="No evidence collected",
                    timestamp=now,
                    url=None,
                )
            )

        # 3. Synthesize
        metadata: dict[str, Any] = {"content_hash": content_hash}
        if hasattr(self._ai, "synthesize_with_fallback"):
            synth = await self._ai.synthesize_with_fallback(
                ai_result, web_results, metadata, timeout=timeout
            )
        else:
            synth = await self._ai.synthesize(ai_result, web_results, metadata)

        if synth.get("error"):
            summary = synth.get("message", synth.get("explanation", summary))
        else:
            verdict = _verdict_str_to_enum(synth.get("verdict", "unverified"))
            confidence = float(synth.get("confidence", 0.0))
            summary = synth.get("explanation", summary)
            toma_scores = _build_toma(
                synth.get("toma_transparency"),
                synth.get("toma_alignment"),
            )

        return InvestigationResult(
            content_hash=content_hash,
            timestamp=now,
            verdict=verdict,
            confidence=confidence,
            toma_scores=toma_scores,
            summary=summary,
            evidence_chain=evidence_chain,
            ai_model=ai_provider,
            da_blob_id=None,
            tx_hash=None,
        )
