"""
Verification endpoints - Phase 1: image upload, DDG search, rule-based analysis, 0G DA/Chain.
"""
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.config import get_settings
from src.services.analysis import VERDICT_NAMES, analyze_investigation
from src.services.storage.temp_storage import save_upload_file, extract_text_from_file
from src.zero_g.da.client import ZeroGDAClient
from src.zero_g.chain.contract import TruthRegistryClient

router = APIRouter()
settings = get_settings()

# Initialize clients (0G optional for demo)
da_client = ZeroGDAClient(settings.OG_DA_ENDPOINT)
chain_client: TruthRegistryClient | None = None
if settings.CONTRACT_ADDRESS and settings.OG_PRIVATE_KEY:
    chain_client = TruthRegistryClient(
        settings.OG_RPC_URL,
        settings.CONTRACT_ADDRESS,
        settings.OG_PRIVATE_KEY,
    )


@router.post("")
async def verify_content(file: UploadFile = File(...)) -> dict[str, Any]:
    """
    Phase 1: Verify image content.

    1. Calculate SHA-256 hash of image
    2. Search DuckDuckGo for fact-checks
    3. Generate investigation JSON (verdict, sources, timestamp)
    4. Publish to 0G DA -> blob_id
    5. Call TruthRegistry.verify() on 0G Chain -> tx_hash

    Returns: hash, verdict, blob_id, tx_hash
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    # Step 1: Save file and compute hash
    file_meta = await save_upload_file(file)
    content_hash = file_meta["content_hash"]
    text_context = extract_text_from_file(
        file_meta["file_path"],
        file_meta["mime_type"],
    )
    search_query = file_meta.get("filename", "") or f"image {content_hash[:16]}"

    # Step 2: Check if already verified (0G Chain)
    tx_hash: str | None = None
    if chain_client:
        existing = chain_client.get_verification(content_hash)
        if existing and existing.get("timestamp", 0) > 0:
            return {
                "status": "already_verified",
                "hash": content_hash,
                "verdict": VERDICT_NAMES.get(existing.get("verdict", 0), "UNVERIFIED"),
                "blob_id": existing.get("daBlobId"),
                "tx_hash": None,
                "message": "Content previously verified on-chain",
            }

    # Step 3: Rule-based analysis with DuckDuckGo search
    investigation = analyze_investigation(
        content_hash=content_hash,
        text_context=text_context,
        search_query=search_query,
    )

    # Step 4: Publish to 0G DA
    investigation_json = {
        "content_hash": content_hash,
        "verdict": investigation["verdict_name"],
        "confidence": investigation["confidence"],
        "sources": investigation["sources"],
        "timestamp": investigation["timestamp"],
        "summary": investigation["summary"],
    }
    da_result = await da_client.submit_blob(investigation_json)
    blob_id = da_result.get("blob_id", "")

    # Step 5: Call TruthRegistry.verify() on 0G Chain (if configured)
    if chain_client:
        chain_result = chain_client.verify(
            content_hash=content_hash,
            da_blob_id=blob_id,
            verdict=investigation["verdict"],
            confidence=investigation["confidence"],
            metadata_uri="",
        )
        tx_hash = chain_result.get("tx_hash")
        if chain_result.get("error"):
            # Graceful: still return result, note chain failure
            tx_hash = None

    return {
        "status": "verified",
        "hash": content_hash,
        "verdict": investigation["verdict_name"],
        "confidence": investigation["confidence"],
        "blob_id": blob_id,
        "tx_hash": tx_hash,
        "sources": investigation["sources"][:5],
        "summary": investigation["summary"],
        "explorer_url": f"https://chainscan-galileo.0g.ai/tx/{tx_hash}" if tx_hash else None,
    }
