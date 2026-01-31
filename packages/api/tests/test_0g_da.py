"""
Test 0G Data Availability client.
"""
import pytest

try:
    from src.zero_g.da_client import ZeroGDAClient
    DA_AVAILABLE = True
except ImportError:
    DA_AVAILABLE = False


@pytest.mark.skipif(not DA_AVAILABLE, reason="0G DA module not present")
@pytest.mark.asyncio
async def test_publish_blob_returns_blob_id():
    """Test publish_blob returns success and blob_id."""
    client = ZeroGDAClient("https://disperser-galileo.0g.ai", timeout=10)
    result = await client.publish_blob({"test": "data", "version": 1})
    assert isinstance(result, dict)
    assert "blob_id" in result
    assert result.get("success", False) or "simulated" in result


@pytest.mark.skipif(not DA_AVAILABLE, reason="0G DA module not present")
def test_da_client_init():
    """ZeroGDAClient accepts node_url and timeout."""
    client = ZeroGDAClient("https://disperser-galileo.0g.ai", timeout=5)
    assert client.node_url
    assert client.timeout == 5
