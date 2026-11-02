"""
QuantumShield FastAPI Backend Main Entrypoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .api.routes import router as api_router
from .api.websocket import router as ws_router
from .core.backend_loader import get_quantum_simulator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("quantumshield")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure simulator is initialized
    try:
        _, name = get_quantum_simulator()
        logger.info(f"QuantumShield backend initialized with {name}")
    except Exception as exc:
        logger.error(f"Simulator initialization warning: {exc}")
    yield
    logger.info("QuantumShield backend shutting down.")


app = FastAPI(
    title="QuantumShield API",
    description="BB84 Quantum Key Distribution Simulation and Real-Time Eavesdropping Attack Detection",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Streamlit and Flutter clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api", tags=["Simulation"])
app.include_router(ws_router, tags=["WebSocket"])


@app.get("/")
def read_root():
    return {
        "project": "QuantumShield",
        "description": "BB84 Quantum Key Distribution & Real-Time Eavesdropping Detection",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
