"""
TruthStream configuration - environment variables and settings.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API
    api_port: int = 8000
    environment: str = "development"

    # 0G Chain (Galileo Testnet)
    og_rpc_url: str = "https://evmrpc-testnet.0g.ai"
    chain_id: int = 16602
    contract_address: Optional[str] = None
    og_private_key: Optional[str] = None

    # 0G Data Availability
    og_da_endpoint: str = "https://disperser-galileo.0g.ai"

    # Optional: AI providers (Phase 2+)
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    perplexity_api_key: Optional[str] = None

    @property
    def API_PORT(self) -> int:
        return self.api_port

    @property
    def ENVIRONMENT(self) -> str:
        return self.environment

    @property
    def OG_RPC_URL(self) -> str:
        return self.og_rpc_url

    @property
    def CONTRACT_ADDRESS(self) -> Optional[str]:
        return self.contract_address

    @property
    def OG_PRIVATE_KEY(self) -> Optional[str]:
        return self.og_private_key

    @property
    def OG_DA_ENDPOINT(self) -> str:
        return self.og_da_endpoint


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
