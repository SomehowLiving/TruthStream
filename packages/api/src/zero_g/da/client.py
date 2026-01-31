"""
0G Data Availability client - publishes investigation reports to 0G DA layer.
Uses disperser-galileo.0g.ai with graceful mock fallback for demo.
"""
import base64
import hashlib
import json
from typing import Any, Optional

import httpx


class ZeroGDAClient:
    """
    0G Data Availability Client for TruthStream.
    Docs: https://docs.0g.ai/developer-hub/building-on-0g/da-integration
    """

    def __init__(self, da_endpoint: str = "https://disperser-galileo.0g.ai") -> None:
        self.da_endpoint = da_endpoint.rstrip("/")

    async def submit_blob(
        self,
        data: dict[str, Any],
        namespace: str = "truthstream-v1",
    ) -> dict[str, Any]:
        """
        Submit investigation data to 0G DA layer.

        Args:
            data: Investigation JSON (verdict, sources, timestamp)
            namespace: DA namespace for blob

        Returns:
            Dict with blob_id, tx_hash, block_height, success, data_hash.
            On failure: returns mock blob_id with success=True for demo.
        """
        json_str = json.dumps(data, default=str)
        data_bytes = json_str.encode("utf-8")
        data_hash = hashlib.sha256(data_bytes).hexdigest()

        try:
            encoded_data = base64.b64encode(data_bytes).decode("ascii")

            async with httpx.AsyncClient() as client:
                # Try HTTP API (0G may use gRPC; HTTP fallback per MVP.md)
                response = await client.post(
                    f"{self.da_endpoint}/v1/disperse_blob",
                    json={
                        "namespace": namespace,
                        "data": encoded_data,
                        "content_type": "application/json",
                    },
                    timeout=30.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "blob_id": result.get("blob_id", f"0x{data_hash[:64]}"),
                        "tx_hash": result.get("tx_hash", "0x" + "0" * 64),
                        "block_height": result.get("block_height", 0),
                        "data_hash": data_hash,
                    }
                else:
                    return self._mock_result(data_hash, f"DA returned {response.status_code}")

        except Exception as e:
            return self._mock_result(data_hash, str(e))

    def _mock_result(self, data_hash: str, error: str) -> dict[str, Any]:
        """Return mock result for demo when DA is unavailable."""
        return {
            "success": True,
            "blob_id": f"0x{data_hash[:64].ljust(64, '0')[:64]}",
            "tx_hash": "0x" + "0" * 64,
            "block_height": 0,
            "data_hash": data_hash,
            "note": f"DA submission simulated (error: {error})",
        }

    async def retrieve_blob(self, blob_id: str) -> Optional[bytes]:
        """Retrieve blob by ID from 0G Storage."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.da_endpoint}/v1/retrieve_blob/{blob_id}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return base64.b64decode(response.json().get("data", ""))
                return None
        except Exception:
            return None
