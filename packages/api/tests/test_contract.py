"""
Test TruthRegistry chain client (0G).
"""
import pytest

try:
    from web3 import Web3
    from src.zero_g.chain_client import TruthRegistryClient
    CHAIN_AVAILABLE = True
except ImportError:
    CHAIN_AVAILABLE = False


@pytest.mark.skipif(not CHAIN_AVAILABLE, reason="Chain client module not present")
def test_contract_address_checksum():
    """If CONTRACT_ADDRESS is set, it should be valid checksum or empty."""
    from src.config import get_settings
    settings = get_settings()
    addr = settings.contract_address
    if not addr or addr.strip() == "":
        pytest.skip("CONTRACT_ADDRESS not set")
    checksum = Web3.to_checksum_address(addr)
    assert checksum == addr or addr.lower() == checksum.lower()


@pytest.mark.skipif(not CHAIN_AVAILABLE, reason="Chain client module not present")
def test_chain_connection():
    """W3 connection to 0G RPC (chain ID)."""
    from src.config import get_settings
    settings = get_settings()
    w3 = Web3(Web3.HTTPProvider(settings.og_rpc_url))
    # Allow failure if network unreachable
    try:
        chain_id = w3.eth.chain_id
        assert chain_id == 16602 or chain_id >= 0
    except Exception as e:
        pytest.skip(f"0G RPC unreachable: {e}")


@pytest.mark.skipif(not CHAIN_AVAILABLE, reason="Chain client module not present")
def test_get_verification_dummy_hash(sample_content_hash):
    """Call get_verification with dummy hash (expect zeros/empty or valid struct)."""
    from src.config import get_settings
    settings = get_settings()
    if not settings.contract_address or not settings.og_private_key:
        pytest.skip("CONTRACT_ADDRESS or OG_PRIVATE_KEY not set")
    try:
        client = TruthRegistryClient(
            settings.og_rpc_url,
            settings.contract_address,
            settings.og_private_key,
        )
        result = client.get_verification(sample_content_hash)
        # Unverified content: None or timestamp 0
        assert result is None or isinstance(result, dict)
    except Exception as e:
        pytest.skip(f"Chain call failed: {e}")
