"""
TruthStream Pydantic schemas – investigation results and verification.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class VerdictCategory(str, Enum):
    VERIFIED = "verified"
    PARTIALLY_FALSE = "partially_false"
    OUT_OF_CONTEXT = "out_of_context"
    MANIPULATED = "manipulated"
    UNVERIFIED = "unverified"


class TOMAScores(BaseModel):
    transparency: int  # 0-100
    ownership: int     # 0-100
    alignment: int     # 0-100
    overall: int       # 0-100


class SourceEvidence(BaseModel):
    type: str  # "ai_analysis", "web_search", etc.
    source: str
    query: Optional[str] = None
    result_summary: str
    timestamp: datetime
    url: Optional[str] = None


class InvestigationResult(BaseModel):
    content_hash: str
    timestamp: datetime
    verdict: VerdictCategory
    confidence: float  # 0.0 - 1.0
    toma_scores: TOMAScores
    summary: str
    evidence_chain: List[SourceEvidence]
    ai_model: str
    da_blob_id: Optional[str] = None
    tx_hash: Optional[str] = None


class VerificationRequest(BaseModel):
    content_url: Optional[str] = None
    content_hash: Optional[str] = None
