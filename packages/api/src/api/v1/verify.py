"""
POST /api/v1/verify – full verification flow: hash → investigate → DA publish → chain record.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException

from src.config import get_settings
from src.models import InvestigationResult
from src.services.analysis import InvestigationEngine, calculate_file_hash
from src.services.ai.unified_ai import get_unified_ai
from src.services.search.unified_search import get_unified_search
from src.zero_g.da_client import ZeroGDAClient
from src.zero_g.chain_client import TruthRegistryClient


router = APIRouter(prefix="/api/v1/verify", tags=["verify"])


@router.post("")
@router.post("/")
async def verify_content(file: UploadFile = File(...)) -> InvestigationResult:
    """
    Accept uploaded file; compute hash, run investigation, publish to 0G DA, record on chain.
    Returns InvestigationResult with verdict, TOMA scores, da_blob_id, tx_hash.
    """
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    
    content_hash = calculate_file_hash(content)
    text_content = content.decode("utf-8", errors="replace")[:8000]

    # Get AI and Search services
    ai = get_unified_ai()
    try:
        search = get_unified_search()
    except Exception:
        search = None
    
    # Run investigation
    engine = InvestigationEngine(ai, search)
    result = await engine.investigate(text_content, content_hash)

    # Publish to 0G DA
    settings = get_settings()
    da_client = ZeroGDAClient(settings.og_da_endpoint, timeout=10)
    payload = result.model_dump(mode="json")
    da_result = await da_client.publish_blob(payload)
    
    blob_id = da_result.get("blob_id", "")
    result.da_blob_id = blob_id

    # Record on 0G Chain (if configured)
    if settings.og_private_key and settings.contract_address:
        try:
            chain = TruthRegistryClient(
                settings.og_rpc_url,
                settings.contract_address,
                settings.og_private_key,
            )
            
            # FIXED: Call certify_truth with correct parameters
            chain_result = await chain.certify_truth(
                content_hash=content_hash,  # FIXED: was file_hash
                blob_id=blob_id,
                confidence=int(result.confidence * 100),  # FIXED: was investigation.confidence
                metadata_uri=f"https://da.0g.ai/blob/{blob_id}"
            )
            
            if not chain_result.get("error") and chain_result.get("tx_hash"):
                result.tx_hash = chain_result["tx_hash"]
                print(f"✅ Chain recorded: {chain_result['tx_hash']}")
            else:
                print(f"⚠️ Chain failed: {chain_result.get('error')}")
                
        except Exception as e:
            print(f"⚠️ Chain error (ok for demo): {e}")
            # Don't fail the whole request if chain fails
            pass

    return result

# """
# POST /api/v1/verify – full verification flow: hash → investigate → DA publish → chain record.
# """
# from fastapi import APIRouter, File, UploadFile, HTTPException

# from src.config import get_settings
# from src.models import InvestigationResult
# from src.services.analysis import InvestigationEngine, calculate_file_hash
# from src.services.ai.unified_ai import get_unified_ai
# from src.services.search.unified_search import get_unified_search
# from src.zero_g.da_client import ZeroGDAClient
# from src.zero_g.chain_client import TruthRegistryClient


# router = APIRouter(prefix="/api/v1/verify", tags=["verify"])


# @router.post("")
# @router.post("/")
# async def verify_content(file: UploadFile = File(...)) -> InvestigationResult:
#     """
#     Accept uploaded file; compute hash, run investigation, publish to 0G DA, record on chain.
#     Returns InvestigationResult with verdict, TOMA scores, da_blob_id, tx_hash.
#     """
#     content = await file.read()
#     if not content:
#         raise HTTPException(status_code=400, detail="Empty file")
#     content_hash = calculate_file_hash(content)
#     text_content = content.decode("utf-8", errors="replace")[:8000]

#     ai = get_unified_ai()
#     try:
#         search = get_unified_search()
#     except Exception:
#         search = None
#     engine = InvestigationEngine(ai, search)
#     result = await engine.investigate(text_content, content_hash)

#     settings = get_settings()
#     da_client = ZeroGDAClient(settings.og_da_endpoint, timeout=10)
#     payload = result.model_dump(mode="json")
#     da_result = await da_client.publish_blob(payload)
#     blob_id = da_result.get("blob_id", "")
#     result.da_blob_id = blob_id

#     if settings.og_private_key and settings.contract_address:
#         try:
#             chain = TruthRegistryClient(
#                 settings.og_rpc_url,
#                 settings.contract_address,
#                 settings.og_private_key,
#             )
#             # chain_result = await chain.verify_content(
#             #     content_hash,
#             #     blob_id,
#             #     result.verdict.value,
#             #     int(result.confidence * 100),
#             # )
#             chain_result = await chain_client.certify_truth(
#                 content_hash=file_hash,
#                 blob_id=da_result["blob_id"],
#                 confidence=int(investigation.confidence * 100),
#                 metadata_uri=f"https://da.0g.ai/blob/{da_result['blob_id']}"  # Optional link
#             )
#             if not chain_result.get("error") and chain_result.get("tx_hash"):
#                 result.tx_hash = chain_result["tx_hash"]
#         except Exception:
#             pass

#     return result
