"""
0G Chain client – TruthRegistry contract (certifyTruth, getCertificate).
"""
import asyncio
from typing import Any

from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount

# ACTUAL ABI FROM YOUR DEPLOYED CONTRACT
TRUTH_REGISTRY_ABI = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "_contentHash", "type": "bytes32"},
            {"internalType": "bytes32", "name": "_daBlobId", "type": "bytes32"},
            {"internalType": "uint8", "name": "_confidence", "type": "uint8"},
            {"internalType": "string", "name": "_metadataURI", "type": "string"},
        ],
        "name": "certifyTruth",
        "outputs": [],
        "stateMutability": "payable",  # IMPORTANT: Requires ETH
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "_contentHash", "type": "bytes32"}],
        "name": "getCertificate",
        "outputs": [
            {
                "components": [
                    {"internalType": "bytes32", "name": "contentHash", "type": "bytes32"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "address", "name": "verifier", "type": "address"},
                    {"internalType": "uint8", "name": "confidenceScore", "type": "uint8"},
                    {"internalType": "bytes32", "name": "daBlobId", "type": "bytes32"},
                    {"internalType": "uint256", "name": "stakeAmount", "type": "uint256"},
                    {"internalType": "bool", "name": "challenged", "type": "bool"},
                    {"internalType": "address", "name": "challenger", "type": "address"},
                    {"internalType": "uint256", "name": "challengeStake", "type": "uint256"},
                    {"internalType": "uint256", "name": "resolutionTime", "type": "uint256"},
                    {"internalType": "string", "name": "metadataURI", "type": "string"},
                ],
                "internalType": "struct TruthRegistry.TruthCertificate",
                "name": "",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "name": "isVerified",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
]


def _hex_to_bytes32(hex_str: str) -> bytes:
    """Convert 64-char hex (with or without 0x) to 32 bytes."""
    s = hex_str.strip()
    if s.startswith("0x"):
        s = s[2:]
    if len(s) != 64:
        raise ValueError(f"content_hash must be 64 hex chars, got {len(s)}")
    return bytes.fromhex(s)


def _string_to_bytes32(s: str) -> bytes:
    """Convert string (like blob_id) to bytes32 (32 bytes)."""
    # Encode string to bytes, pad or truncate to 32 bytes
    encoded = s.encode("utf-8")
    if len(encoded) > 32:
        # If longer than 32 bytes, hash it
        from hashlib import sha256

        return sha256(encoded).digest()
    # Pad with zeros to 32 bytes
    return encoded.ljust(32, b"\0")


class TruthRegistryClient:
    """TruthRegistry contract on 0G Chain: certifyTruth, getCertificate."""

    def __init__(
        self,
        rpc_url: str,
        contract_address: str,
        private_key: str,
    ) -> None:
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract_address = Web3.to_checksum_address(contract_address)
        self._account: LocalAccount = Account.from_key(private_key)
        self._contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=TRUTH_REGISTRY_ABI,
        )

    def get_certificate(self, content_hash: str) -> dict[str, Any] | None:
        """Sync: get certificate for content_hash. Returns None if not found."""
        try:
            h = _hex_to_bytes32(content_hash)
            # Returns tuple: (contentHash, timestamp, verifier, confidenceScore, daBlobId, stakeAmount, challenged, challenger, challengeStake, resolutionTime, metadataURI)
            cert = self._contract.functions.getCertificate(h).call()
            
            if cert[1] == 0:  # timestamp is 0
                return None
            
            return {
                "contentHash": cert[0].hex(),
                "timestamp": cert[1],
                "verifier": cert[2],
                "confidenceScore": cert[3],
                "daBlobId": cert[4].hex(),  # This is bytes32, convert to hex string
                "stakeAmount": cert[5],
                "challenged": cert[6],
                "challenger": cert[7],
                "challengeStake": cert[8],
                "resolutionTime": cert[9],
                "metadataURI": cert[10],
            }
        except Exception as e:
            print(f"Error getting certificate: {e}")
            return None

    async def certify_truth(
        self,
        content_hash: str,
        blob_id: str,
        confidence: int,
        metadata_uri: str = "",
    ) -> dict[str, Any]:
        """
        Async: record verification on chain. Runs in thread to avoid blocking.
        Returns dict with tx_hash, explorer_url; or error key on failure.
        
        IMPORTANT: Sends 0.01 ETH (0.01 * 10^18 wei) as stake.
        """
        def _tx() -> dict[str, Any]:
            # Convert inputs
            h = _hex_to_bytes32(content_hash)
            blob_bytes = _string_to_bytes32(blob_id)  # blob_id is bytes32 in contract
            c = max(0, min(100, confidence))
            
            # Check if already verified
            is_verified = self._contract.functions.isVerified(h).call()
            if is_verified:
                return {"error": "Content already verified", "tx_hash": None}
            
            print(f"DEBUG: Calling certifyTruth with:")
            print(f"  contentHash: {h.hex()}")
            print(f"  daBlobId: {blob_bytes.hex()}")
            print(f"  confidence: {c}")
            print(f"  metadataURI: {metadata_uri}")
            print(f"  value: 0.01 ETH")

            tx = self._contract.functions.certifyTruth(
                h, 
                blob_bytes, 
                c, 
                metadata_uri
            ).build_transaction(
                {
                    "from": self._account.address,
                    "nonce": self.w3.eth.get_transaction_count(self._account.address),
                    "gas": 500_000,
                    "gasPrice": self.w3.to_wei("10", "gwei"),
                    "value": self.w3.to_wei("0.01", "ether"),  # REQUIRED STAKE
                }
            )
            signed = self._account.sign_transaction(tx)
            tx_hash_bytes = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            tx_hash = self.w3.to_hex(tx_hash_bytes)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            
            explorer_url = f"https://chainscan-galileo.0g.ai/tx/{tx_hash}"
            return {
                "tx_hash": tx_hash,
                "explorer_url": explorer_url,
                "gas_used": receipt.gasUsed,
                "block_number": receipt.blockNumber,
            }

        try:
            result = await asyncio.to_thread(_tx)
            return result
        except Exception as e:
            return {"error": str(e), "tx_hash": None, "explorer_url": None}
            
# """
# 0G Chain client – TruthRegistry contract (verifyContent, getVerification).
# """
# import asyncio
# from typing import Any

# from web3 import Web3
# from eth_account import Account
# from eth_account.signers.local import LocalAccount

# # TruthRegistry ABI: verifyContent(bytes32, string, uint8, uint8), getVerification(bytes32)
# TRUTH_REGISTRY_ABI = [
#     {
#         "inputs": [
#             {"name": "contentHash", "type": "bytes32"},
#             {"name": "blobId", "type": "string"},
#             {"name": "verdict", "type": "uint8"},
#             {"name": "confidence", "type": "uint8"},
#         ],
#         "name": "verifyContent",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [{"name": "contentHash", "type": "bytes32"}],
#         "name": "getVerification",
#         "outputs": [
#             {"name": "blobId", "type": "string"},
#             {"name": "verdict", "type": "uint8"},
#             {"name": "confidence", "type": "uint8"},
#             {"name": "timestamp", "type": "uint256"},
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
# ]

# VERDICT_TO_UINT = {
#     "unverified": 0,
#     "verified": 1,
#     "partially_false": 2,
#     "out_of_context": 3,
#     "manipulated": 4,
# }


# def _hex_to_bytes32(hex_str: str) -> bytes:
#     """Convert 64-char hex (with or without 0x) to 32 bytes."""
#     s = hex_str.strip()
#     if s.startswith("0x"):
#         s = s[2:]
#     if len(s) != 64:
#         raise ValueError("content_hash must be 64 hex chars")
#     return bytes.fromhex(s)


# class TruthRegistryClient:
#     """TruthRegistry contract on 0G Chain: verifyContent, getVerification."""

#     def __init__(
#         self,
#         rpc_url: str,
#         contract_address: str,
#         private_key: str,
#     ) -> None:
#         self.w3 = Web3(Web3.HTTPProvider(rpc_url))
#         self.contract_address = Web3.to_checksum_address(contract_address)
#         self._account: LocalAccount = Account.from_key(private_key)
#         self._contract = self.w3.eth.contract(
#             address=self.contract_address,
#             abi=TRUTH_REGISTRY_ABI,
#         )

#     def get_verification(self, content_hash: str) -> dict[str, Any] | None:
#         """Sync: get verification for content_hash. Returns None or dict (blobId, verdict, confidence, timestamp)."""
#         try:
#             h = _hex_to_bytes32(content_hash)
#             blob_id, verdict, confidence, timestamp = self._contract.functions.getVerification(h).call()
#             if timestamp == 0:
#                 return None
#             return {
#                 "blobId": blob_id,
#                 "verdict": verdict,
#                 "confidence": confidence,
#                 "timestamp": timestamp,
#             }
#         except Exception:
#             return None

#     async def verify_content(
#         self,
#         content_hash: str,
#         blob_id: str,
#         verdict: str,
#         confidence: int,
#     ) -> dict[str, Any]:
#         """
#         Async: record verification on chain. Runs in thread to avoid blocking.
#         Returns dict with tx_hash, explorer_url; or error key on failure.
#         """
#         def _tx() -> dict[str, Any]:
#             h = _hex_to_bytes32(content_hash)
#             v = VERDICT_TO_UINT.get((verdict or "").strip().lower(), 0)
#             c = max(0, min(100, confidence))
#             tx = self._contract.functions.verifyContent(h, blob_id, v, c).build_transaction(
#                 {
#                     "from": self._account.address,
#                     "nonce": self.w3.eth.get_transaction_count(self._account.address),
#                     "gas": 500_000,
#                     "gasPrice": self.w3.to_wei("10", "gwei"),
#                 }
#             )
#             signed = self._account.sign_transaction(tx)
#             tx_hash_bytes = self.w3.eth.send_raw_transaction(signed.raw_transaction)
#             tx_hash = self.w3.to_hex(tx_hash_bytes)
#             # Galileo explorer
#             explorer_url = f"https://chainscan-galileo.0g.ai/tx/{tx_hash}"
#             return {"tx_hash": tx_hash, "explorer_url": explorer_url}

#         try:
#             result = await asyncio.to_thread(_tx)
#             return result
#         except Exception as e:
#             return {"error": str(e), "tx_hash": None, "explorer_url": None}
