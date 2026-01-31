from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.endpoints import verify

app = FastAPI(
    title="TruthStream API",
    description="Decentralized AI Verification on 0G",
    version="0.1.0"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(verify.router, prefix="/api/v1/verify", tags=["verification"])
# Alias for acceptance criteria: POST /verify
app.include_router(verify.router, prefix="/verify", tags=["verification"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "truthstream-api"}

if __name__ == "__main__":
    import uvicorn
    from src.config import get_settings

    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT == "development"
    )