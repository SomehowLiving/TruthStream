# Tools Used & External Services 🧰

This file documents the development, testing, blockchain, and AI tooling used by TruthStream.

---

## Development Tools
| Tool | Role |
|------|------|
| VS Code / Cursor | Primary IDE / editor |
| Git | Version control |
| Make | Task runner (see `packages/api/Makefile`) |
| Node.js / npm | Frontend package management & dev server |
| Python / venv | Backend runtime & environment |


## Frontend Libraries (selected)
- React 18, Vite, Tailwind CSS
- Axios (HTTP), react-dropzone (uploads), lucide-react (icons)

## Backend Libraries (selected)
- FastAPI, Uvicorn, Pydantic, Web3.py, python-multipart
- LLM SDKs: `anthropic` and `groq` (optional via env keys)

---

## Testing & Debugging
| Tool | Purpose |
|------|---------|
| pytest / pytest-asyncio | Unit & async tests (`packages/api/tests`) |
| curl / httpie / Postman | API integration testing |
| integration_test.py | Project integration script for end-to-end flow (uploads, DA publish, optional chain record)

---

## Blockchain Tools
| Tool | Purpose |
|------|---------|
| web3.py | Interact with 0G Galileo Testnet & contracts |
| 0G Explorer (Chainscan) | Monitor transactions and tx URLs (`https://chainscan-galileo.0g.ai/tx/{tx_hash}`) |
| MetaMask (recommended) | Wallet when interacting with chain in browser demos |

**Contract**: `TruthRegistry` — Solidity contract lives in `packages/contracts/src/TruthStream.sol`.

**Deployed address** (from repo `.env`): `0x6bE7D6A9457634c2BFbcca5b224b52aAAa70aa05` (Galileo Testnet)

---

## AI Tools & Services
- Anthropic (Claude 3.5) — primary LLM for deep analysis (requires `ANTHROPIC_API_KEY`)
- Groq — optional LLM provider fallback
- Tavily / DuckDuckGo — web search sources

> API keys are read from `.env` in `packages/api/`. Do not commit keys; use environment variables instead.

---

## Utilities
- Tesseract OCR (if used for image text extraction) — not required by repo but commonly used for OCR steps
- Redis (optional) — caching, configurable via `REDIS_URL`

---

## Running locally (quick start)
**Backend**
```bash
cd packages/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make run
```
**Frontend**
```bash
cd frontend
npm install
npm run dev
```

