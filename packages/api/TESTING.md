# TruthStream Backend – Testing Guide

## Prerequisites

- **Python**: 3.11+
- **0G testnet**: Funded wallet for chain recording (optional; mock mode if not set)
- **Redis**: Not required for current tests (no cache in scope)
- **Environment**: Copy `.env.example` to `.env` and set API keys as needed

## Environment Variables

Create `.env` from this template:

```bash
# API
API_PORT=8000
ENVIRONMENT=development

# 0G Chain (Galileo Testnet)
OG_RPC_URL=https://evmrpc-testnet.0g.ai
CHAIN_ID=16602
CONTRACT_ADDRESS=    # Deployed TruthRegistry address
OG_PRIVATE_KEY=      # 0x... (for chain recording)

# 0G Data Availability
OG_DA_ENDPOINT=https://disperser-galileo.0g.ai

# AI (at least one for full flow)
ANTHROPIC_API_KEY=
GROQ_API_KEY=

# Search
TAVILY_API_KEY=
```

- **Unit tests**: Can run with no keys; tests that need keys will skip or mock and print a warning.
- **Integration test**: Needs at least one AI key for the full flow; 0G and search are optional (mock/skip).

## Installation

```bash
cd packages/api
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` includes `pytest`, `pytest-asyncio`, and `httpx` for tests. If your env omits them, run:

```bash
pip install pytest pytest-asyncio httpx
```

## Running Tests

### Unit tests (pytest)

```bash
cd packages/api
# From repo root, with src on path:
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/src"
python -m pytest tests/ -v
```

### Integration test (standalone)

```bash
cd packages/api
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/src"
python integration_test.py
```

### Scripts (Makefile / run_tests.sh)

```bash
make test-unit        # pytest tests/
make test-integration # python integration_test.py
make run              # uvicorn (if main.py present)
make check            # curl /health
```

Or use the shell script:

```bash
./run_tests.sh unit
./run_tests.sh integration
```

## Test Descriptions

| Test File          | What it does |
|--------------------|--------------|
| `test_config.py`   | Loads settings, checks env (masked keys), verifies 0G chain ID. |
| `test_ai.py`       | Calls UnifiedAI with a sample claim; checks fallback; asserts verdict/confidence in response. Skips if no AI keys. |
| `test_search.py`   | Runs search for a fact-check query; asserts `sources` in result. Skips if search module or Tavily/DDG unavailable. |
| `test_0g_da.py`    | Publishes a dummy blob to 0G DA; asserts `blob_id`. Skips if 0G DA module missing. |
| `test_contract.py` | Connects to TruthRegistry, calls getVerification with dummy hash (expect zeros/empty). Checks contract address checksum. Skips if chain client missing. |
| `test_analysis.py` | Runs InvestigationEngine on sample text; asserts TOMA scores and evidence chain. Skips if analysis/engine missing. |

## Expected Output (examples)

- **test_config**: Prints masked API keys (e.g. `ANTHROPIC=sk-ant-***`) and `CHAIN_ID=16602`.
- **test_ai**: Response dict with `provider`, `claims` (list), and either analysis fields or fallback verdict/confidence.
- **test_search**: Response with `sources` (list), optionally `answer` and `provider`.
- **test_0g_da**: `success=True`, `blob_id` present (or mock blob_id if DA unavailable).
- **test_contract**: No exception; getVerification returns zeros/empty or valid struct; contract address is checksummed.
- **test_analysis**: InvestigationResult with `toma_scores`, `evidence_chain` length ≥ 1.

## Integration Test Flow

1. Create dummy file `test_image.txt` with content e.g. "PM announces new policy".
2. Compute content hash (e.g. SHA-256).
3. Run investigation (AI + optional search).
4. Publish to 0G DA (or mock).
5. Optionally record on 0G chain (or mock if no key).
6. Optionally verify certificate retrieval.

Printed output includes:

- Content hash
- AI provider used (Anthropic/Groq)
- Search provider used (Tavily/DDG) if applicable
- Verdict and TOMA score
- 0G DA blob ID
- 0G chain tx (or mock)
- Explorer URL when tx is present
- Total time (target &lt; 5 s where applicable)

## Troubleshooting

| Error | Cause | Fix |
|-------|--------|-----|
| `ModuleNotFoundError: src.*` | Wrong working directory or PYTHONPATH | Run from `packages/api` with `PYTHONPATH=$(pwd)/src` or use `run_tests.sh`. |
| `ANTHROPIC_API_KEY not configured` | No AI key in `.env` | Set at least one of `ANTHROPIC_API_KEY` or `GROQ_API_KEY` for AI tests. |
| `503 AI analysis failed` | All AI providers failed or no keys | Check keys and network; tests will skip or mock when keys missing. |
| `Connection refused` (0G RPC) | RPC down or wrong URL | Use `OG_RPC_URL=https://evmrpc-testnet.0g.ai` and retry; chain tests skip if unreachable. |
| `Invalid private key` | Bad `OG_PRIVATE_KEY` | Use hex string `0x...`; chain recording is optional (mock if not set). |
| `getVerification` / `getCertificate` mismatch | ABI vs contract name | Ensure chain client uses the same contract (TruthRegistry) and method name as deployed contract. |

## Codebase Layout (for reference)

```
packages/api/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── models/           # certificate.py, etc.
│   ├── services/
│   │   ├── ai/           # anthropic_client, groq_client, unified_ai
│   │   ├── search/       # tavily_client, duckduckgo_client, unified_search
│   │   └── analysis.py    # InvestigationEngine, calculate_file_hash
│   ├── zero_g/           # da_client.py, chain_client.py (or 0g/)
│   └── api/v1/verify.py
├── tests/
├── integration_test.py
├── run_tests.sh
├── .env.example
└── requirements.txt
```

Tests are written to skip missing modules (e.g. no `zero_g` or `search`) so that both the current partial backend and the full backend pass.
