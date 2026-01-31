# TruthStream Technology Stack 🔧

## Overview
TruthStream is a full-stack hackathon project for decentralized AI-backed content verification. It consists of a React + TypeScript frontend (Vite + Tailwind) that uploads content to a FastAPI backend which runs AI analysis, optional web search, synthesizes a verdict and TOMA scores, stores an investigation snapshot in 0G DA, and optionally anchors the result on the 0G Galileo Testnet via a TruthRegistry smart contract.

---

## Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| react | ^18.2.0 | UI library |
| react-dom | ^18.2.0 | DOM rendering |
| vite | ^5.1.7 | Dev server & bundler |
| typescript | ^5.4.2 | Static types |
| tailwindcss | ^3.4.17 | Utility-first CSS framework |
| postcss | ^8.4.24 | CSS processing |
| autoprefixer | ^10.4.14 | CSS vendor prefixes |
| axios | ^1.7.2 | HTTP client for API calls |
| react-dropzone | ^14.2.4 | Drag-and-drop uploads |
| lucide-react | ^0.269.0 | Icons |
| clsx | ^1.2.1 | Classname helper |
| tailwind-merge | ^1.14.0 | Class merging utility |

> Project: `frontend/` — run with `npm install && npm run dev` (http://localhost:5173)

---

## Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| fastapi | >=0.100.0 | Web API framework |
| uvicorn | >=0.22.0 | ASGI server |
| pydantic | >=2.0 | Validation and models |
| pydantic-settings | >=2.0 | Settings via env files |
| python-dotenv | >=1.0 | `.env` loading |
| httpx | >=0.24.0 | Async HTTP client |
| python-multipart | >=0.0.6 | Multipart/form-data file uploads |
| anthropic | >=0.18.0 | Anthropic LLM client (optional) |
| web3 | >=6.0.0 | Ethereum/0G chain interaction |
| eth-account | >=0.10.0 | Account management for signing txs |
| duckduckgo-search | >=6.0.0 | Web search fallback |
| pytest / pytest-asyncio | >=7.0.0 / >=0.21.0 | Tests |

> Project: `packages/api/` — run with `make run` or `uvicorn src.main:app --reload --port 8000` (http://localhost:8000)

---

## Blockchain (0G)
| Component | Network | Purpose |
|-----------|---------|---------|
| 0G Chain (TruthRegistry) | Galileo Testnet | Smart contract registry for verified content (`certifyTruth`, `challengeTruth`, etc.)
| 0G DA (Disperser) | Disperser / DA node | Stores investigation payloads as blobs

**Deployed contract** (from repo `.env`): `0x6bE7D6A9457634c2BFbcca5b224b52aAAa70aa05` (TruthRegistry, Galileo Testnet)

RPC/DA endpoints (defaults in `packages/api/.env` & `config`):
- RPC: `https://evmrpc-testnet.0g.ai`
- DA endpoint: `https://disperser-galileo.0g.ai`

---

## AI / ML Services
| Service | Model / Notes | Purpose | Fallback |
|---------|---------------|---------|----------|
| Anthropic | Claude 3.5 (configured via `ANTHROPIC_API_KEY`) | Deep analysis & synthesis | Groq
| Groq | (API key configurable) | Alternative LLM provider | -
| Tavily | Search API (optional) | Web fact-checking and source discovery | DuckDuckGo search fallback

> API keys are configured via environment variables (e.g. `ANTHROPIC_API_KEY`, `GROQ_API_KEY`, `TAVILY_API_KEY`). Do NOT commit secrets to git.

---

## Infrastructure & Tooling
| Component | Purpose |
|-----------|---------|
| Git / GitHub | Version control & repo hosting |
| Make | Task runner (install, run, tests) |
| Docker (optional) | Containerization (not required by repo) |
| Redis | Optional caching (repo references `REDIS_URL`) |

---

## Notes & Setup Tips 💡
- The backend reads configuration from `.env` (see `packages/api/.env.example`). Keep secrets out of source control.
- Dev CORS issues are handled via Vite proxy (`frontend/vite.config.ts`) and backend CORS middleware (`packages/api/src/main.py`).
- Contract code lives under `packages/contracts` and the Solidity contract is `TruthRegistry` (see `packages/contracts/src/TruthStream.sol`).

---

