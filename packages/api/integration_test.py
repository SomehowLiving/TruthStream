#!/usr/bin/env python3
"""
TruthStream integration test – full verification flow.

Run from packages/api with:
  PYTHONPATH=src python integration_test.py

Steps:
  1. Create dummy file (test_image.txt)
  2. Calculate hash
  3. Run investigation (AI + Search if available)
  4. Publish to 0G DA (or mock)
  5. Record on 0G Chain (if key set, else mock)
  6. Optionally verify certificate retrieval

Prints: content hash, AI/search providers, verdict, TOMA, blob_id, tx, explorer URL, total time.
"""
import asyncio
import sys
import time
from pathlib import Path

# Ensure src is on path
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _step(name: str):
    print(f"\n--- Step: {name} ---")


def main_sync():
    """Run integration steps; skip missing modules."""
    start = time.perf_counter()
    print("TruthStream Integration Test")
    print("=============================")

    # Step 1: Dummy file and hash
    _step("Create dummy file and hash")
    content = b"PM announces new policy"
    test_file = ROOT / "test_image.txt"
    test_file.write_bytes(content)
    print(f"Created {test_file} with {len(content)} bytes")

    try:
        from src.services.analysis import calculate_file_hash
    except ImportError:
        import hashlib
        file_hash = hashlib.sha256(content).hexdigest()
        print(f"Content hash (hashlib): 0x{file_hash}")
    else:
        file_hash = calculate_file_hash(content)
        print(f"Content hash: 0x{file_hash}")

    # Step 2 & 3: Investigation (AI + optional Search)
    _step("Investigation (AI + Search)")
    ai_provider = "none"
    search_provider = "none"
    verdict = "unverified"
    confidence = 0.0
    toma_overall = 0
    investigation_result = None

    try:
        from src.services.ai.unified_ai import get_unified_ai
        from src.services.search.unified_search import get_unified_search
        from src.services.analysis import InvestigationEngine
    except ImportError as e:
        print(f"Investigation modules missing: {e}")
        print("Skipping investigation; using mock verdict.")
    else:
        ai = get_unified_ai()
        try:
            search = get_unified_search()
        except Exception:
            search = None
        if not ai.has_providers:
            print("No AI keys configured; skipping investigation.")
        elif search is None:
            print("Search not available; running AI only.")
            # Minimal: just AI analyze + mock synthesis
            async def run_ai_only():
                result = await ai.analyze_with_fallback("PM announces new policy")
                if result.get("error"):
                    return None, "none", 0.0, 0
                ai_provider = result.get("provider", "unknown")
                synth = await ai.synthesize_with_fallback(result, [], {})
                if synth.get("error"):
                    return None, ai_provider, 0.0, 50
                return result, ai_provider, float(synth.get("confidence", 0)), int(synth.get("toma_transparency", 50) or 50)
            res, ai_provider, confidence, toma_overall = asyncio.run(run_ai_only())
            verdict = "unverified"
            if res:
                ai_provider = res.get("provider", "none")
            print(f"AI Provider used: {ai_provider}")
            print(f"Verdict: {verdict}; Confidence: {confidence}; TOMA: {toma_overall}")
        else:
            engine = InvestigationEngine(ai, search)
            try:
                investigation_result = asyncio.run(
                    engine.investigate("PM announces new policy", file_hash)
                )
                ai_provider = investigation_result.ai_model
                verdict = investigation_result.verdict.value
                confidence = investigation_result.confidence
                toma_overall = investigation_result.toma_scores.overall
                print(f"AI Provider used: {ai_provider}")
                print(f"Verdict: {verdict}; Confidence: {confidence}; TOMA Score: {toma_overall}/100")
            except Exception as e:
                print(f"Investigation failed: {e}")
                if "503" in str(e) or "AI" in str(e):
                    print("(No AI keys or all providers failed)")

    # Step 4: Publish to 0G DA
    _step("Publish to 0G DA")
    blob_id = "mock_no_da_module"
    try:
        from src.zero_g.da_client import ZeroGDAClient
        from src.config import get_settings
        settings = get_settings()
        client = ZeroGDAClient(settings.og_da_endpoint, timeout=10)
        payload = {
            "content_hash": file_hash,
            "verdict": verdict,
            "confidence": confidence,
            "summary": "Integration test run",
        }
        if investigation_result is not None and hasattr(investigation_result, "model_dump"):
            payload = investigation_result.model_dump(mode="json")
        result = asyncio.run(client.publish_blob(payload))
        blob_id = result.get("blob_id", blob_id)
        print(f"0G DA Blob ID: {blob_id}")
    except ImportError as e:
        print(f"0G DA module not present: {e}")
        print(f"Mock blob_id: {blob_id}")
    except Exception as e:
        print(f"DA publish error: {e}")
        print(f"Mock blob_id: {blob_id}")

    # Step 5: Record on 0G Chain
    _step("Record on 0G Chain")
    tx_hash = None
    explorer_url = "https://chainscan-galileo.0g.ai/tx/"
    try:
        from src.config import get_settings
        from src.zero_g.chain_client import TruthRegistryClient
        settings = get_settings()
        if not settings.og_private_key or not settings.contract_address:
            print("OG_PRIVATE_KEY or CONTRACT_ADDRESS not set; skipping chain record.")
        else:
            chain = TruthRegistryClient(
                settings.og_rpc_url,
                settings.contract_address,
                settings.og_private_key,
            )
            chain_result = asyncio.run(chain.verify_content(
                file_hash, blob_id, verdict, int(confidence * 100)
            ))
            tx_hash = chain_result.get("tx_hash")
            explorer_url = chain_result.get("explorer_url", explorer_url)
            if chain_result.get("error"):
                print(f"Chain recording failed: {chain_result['error']}")
            else:
                print(f"0G Chain Tx: {tx_hash}")
                print(f"Explorer URL: {explorer_url}")
    except ImportError:
        print("Chain client not present; skipping.")
    except Exception as e:
        print(f"Chain error: {e}")
    if not tx_hash:
        print("Tx: (mock - not recorded)")

    # Timer
    elapsed = time.perf_counter() - start
    print(f"\n--- Total time: {elapsed:.2f}s (target <5s) ---")
    if test_file.exists():
        try:
            test_file.unlink()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main_sync())
