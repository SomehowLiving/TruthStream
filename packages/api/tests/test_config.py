"""
Test config loading and 0G connection settings.
"""
import pytest

from src.config import get_settings


def test_load_settings():
    """Load settings and verify no crash."""
    settings = get_settings()
    assert settings is not None


def test_api_port_default():
    """API port defaults to 8000."""
    settings = get_settings()
    assert settings.api_port == 8000


def test_chain_id_0g_galileo():
    """0G Galileo testnet chain ID is 16602."""
    settings = get_settings()
    assert settings.chain_id == 16602


def test_og_rpc_url_set():
    """OG RPC URL is set."""
    settings = get_settings()
    assert settings.og_rpc_url
    assert "evmrpc" in settings.og_rpc_url or "0g" in settings.og_rpc_url.lower()


def test_og_da_endpoint_set():
    """OG DA endpoint is set."""
    settings = get_settings()
    assert settings.og_da_endpoint
    assert "disperser" in settings.og_da_endpoint or "0g" in settings.og_da_endpoint.lower()


def test_masked_keys_print(capsys):
    """Print masked API keys for audit (no assertion on value)."""
    settings = get_settings()
    masked = []
    if settings.anthropic_api_key:
        masked.append(f"ANTHROPIC={settings.anthropic_api_key[:8]}***")
    if settings.groq_api_key:
        masked.append(f"GROQ={settings.groq_api_key[:8]}***")
    if settings.tavily_api_key:
        masked.append(f"TAVILY={settings.tavily_api_key[:8]}***")
    if settings.og_private_key:
        masked.append("OG_PRIVATE_KEY=0x***")
    if settings.contract_address:
        masked.append(f"CONTRACT={settings.contract_address[:10]}...")
    # Just ensure we can read; don't leak keys
    assert isinstance(masked, list)
