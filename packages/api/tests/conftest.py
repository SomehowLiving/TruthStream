"""
Pytest configuration and fixtures for TruthStream backend tests.
"""
import sys
from pathlib import Path

# Add packages/api/src to path so "src.*" imports work
api_src = Path(__file__).resolve().parent.parent / "src"
if str(api_src) not in sys.path:
    sys.path.insert(0, str(api_src.parent))

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: mark test as integration (slower, may need keys)")


@pytest.fixture
def sample_text():
    return "Test claim: Earth is flat"


@pytest.fixture
def sample_content_hash():
    return "a" * 64
