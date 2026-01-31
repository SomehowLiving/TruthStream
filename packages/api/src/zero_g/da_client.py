"""
0G Data Availability client – publish blobs with HTTP/simulated fallback.
"""
import json
import time
from typing import Any

import httpx


class ZeroGDAClient:
    """Publish blobs to 0G DA; returns blob_id. Falls back to simulated blob on failure."""

    def __init__(self, node_url: str, timeout: float = 10.0) -> None:
        self.node_url = node_url.rstrip("/")
        self.timeout = timeout

    async def publish_blob(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Publish payload to 0G DA. Returns dict with blob_id (and success if real).
        On network/API failure, returns simulated blob_id so callers can continue.
        """
        payload_bytes = json.dumps(data, default=str).encode("utf-8")
        try:
            # Try REST-style POST if the endpoint supports it (testnet may expose one)
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.node_url}/v1/blobs",
                    content=payload_bytes,
                    headers={"Content-Type": "application/json"},
                )
                if resp.status_code in (200, 201, 202):
                    out = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                    blob_id = out.get("blob_id") or out.get("id") or out.get("blobId")
                    if blob_id:
                        return {"blob_id": blob_id, "success": True}
                # Fallback: generate deterministic id from content
                blob_id = f"simulated_{hash(payload_bytes) & 0x7FFFFFFF:08x}_{int(time.time())}"
                return {"blob_id": blob_id, "success": False, "simulated": True}
        except Exception:
            blob_id = f"simulated_{hash(payload_bytes) & 0x7FFFFFFF:08x}_{int(time.time())}"
            return {"blob_id": blob_id, "success": False, "simulated": True}
