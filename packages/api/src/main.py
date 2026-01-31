"""
TruthStream FastAPI app – CORS, /health, /api/v1/verify.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.api.v1.verify import router as verify_router


def create_app() -> FastAPI:
    app = FastAPI(title="TruthStream API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(verify_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.on_event("startup")
    def startup():
        settings = get_settings()
        ai_ok = bool(settings.anthropic_api_key or settings.groq_api_key)
        search_ok = bool(settings.tavily_api_key)
        og_ok = bool(settings.og_private_key and settings.contract_address)
        # Optional: log config status
        # print(f"AI: {ai_ok}, Search: {search_ok}, 0G Chain: {og_ok}")

    return app


app = create_app()
