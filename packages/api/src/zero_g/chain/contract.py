"""
TruthRegistry contract client - aligns with TruthRegistry.sol (MVP.md).
Calls verifyContent(contentHash, daBlobId, verdict, confidence, metadataURI).
"""
from typing import Any, Optional

from eth_account import Account
from web3 import Web3

# ABI for TruthRegistry.verifyContent (MVP.md)
TRUTH_REGISTRY_ABI = [
    {
        "inputs": [
            {"name": "contentHash", "type": "bytes32"},
            {"name": "daBlobId", "type": "bytes32"},
            {"name": "verdict", "type": "uint8"},
            {"name": "confidence", "type": "uint8"},
            {"name": "metadataURI", "type": "string"},
        ],
        "name": "verifyContent",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [{"name": "contentHash", "type": "bytes32"}],
        "name": "getVerification",
        "outputs": [
            {"name": "verifier", "type": "address"},
            {"name": "timestamp", "type": "uint256"},
            {"name": "stakeAmount", "type": "uint256"},
            {"name": "verdict", "type": "uint8"},
            {"name": "confidence", "type": "uint8"},
            {"name": "daBlobId", "type": "bytes32"},
            {"name": "contentHash", "type": "bytes32"},
            {"name": "challenged", "type": "bool"},
            {"name": "challengeDeadline", "type": "uint256"},
            {"name": "metadataURI", "type": "string"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]

# Verdict enum from TruthRegistry.sol
VERDICT_UNVERIFIED = 0
VERDICT_VERIFIED = 1
VERDICT_PARTIALLY_FALSE = 2
VERDICT_OUT_OF_CONTEXT = 3
VERDICT_MANIPULATED = 4


class TruthRegistryClient:
    """Web3.py client for TruthRegistry on 0G Chain."""

    def __init__(
        self,
        rpc_url: str,
        contract_address: str,
        private_key: str,
    ) -> None:
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key)
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=TRUTH_REGISTRY_ABI,
        )

    def verify(
        self,
        content_hash: str,
        da_blob_id: str,
        verdict: int,
        confidence: int,
        metadata_uri: str = "",
    ) -> dict[str, Any]:
        """
        Call TruthRegistry.verifyContent on 0G Chain.

        Args:
            content_hash: SHA-256 hash of content (hex, with or without 0x)
            da_blob_id: 0G DA blob ID (hex or string, padded to 32 bytes)
            verdict: 0-4 (UNVERIFIED, VERIFIED, PARTIALLY_FALSE, OUT_OF_CONTEXT, MANIPULATED)
            confidence: 0-100
            metadata_uri: Optional URI to full investigation

        Returns:
            Dict with tx_hash, status. On error: tx_hash=None, error=str.
        """
        try:
            content_hash_hex = content_hash.replace("0x", "")
            if len(content_hash_hex) != 64:
                return {"tx_hash": None, "error": "content_hash must be 32 bytes (64 hex chars)"}

            content_hash_bytes = bytes.fromhex(content_hash_hex)
            da_blob_bytes = self._to_bytes32(da_blob_id)
            confidence = min(100, max(0, confidence))

            tx = self.contract.functions.verifyContent(
                content_hash_bytes,
                da_blob_bytes,
                verdict,
                confidence,
                metadata_uri,
            ).build_transaction(
                {
                    "from": self.account.address,
                    "nonce": self.w3.eth.get_transaction_count(self.account.address),
                    "gas": 200000,
                    "gasPrice": self.w3.to_wei("1", "gwei"),
                    "value": self.w3.to_wei("0.01", "ether"),
                }
            )

            signed = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            return {"tx_hash": tx_hash.hex(), "status": "pending"}
        except Exception as e:
            return {"tx_hash": None, "error": str(e)}

    def get_verification(self, content_hash: str) -> Optional[dict[str, Any]]:
        """Check if content already verified on-chain."""
        try:
            content_hash_hex = content_hash.replace("0x", "")
            if len(content_hash_hex) != 64:
                return None
            content_hash_bytes = bytes.fromhex(content_hash_hex)

            result = self.contract.functions.getVerification(content_hash_bytes).call()
            if result[1] == 0:
                return None

            return {
                "verifier": result[0],
                "timestamp": result[1],
                "stakeAmount": result[2],
                "verdict": result[3],
                "confidence": result[4],
                "daBlobId": result[5].hex(),
                "contentHash": result[6].hex(),
                "challenged": result[7],
                "challengeDeadline": result[8],
                "metadataURI": result[9],
            }
        except Exception:
            return None

    def _to_bytes32(self, value: str) -> bytes:
        """Convert hex string or short string to 32 bytes."""
        s = value.replace("0x", "")
        if len(s) >= 64:
            return bytes.fromhex(s[:64])
        return s.encode().ljust(32, b"\0")[:32]
