# orchestrator/main.py

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from orchestrator.api.routes import router as api_router
from orchestrator.core.grpc_client import grpc_client
from orchestrator.core.config import LOG_LEVEL
from orchestrator.core.logging import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the application's startup and shutdown events."""
    setup_logging(LOG_LEVEL)
    logging.info("Orchestrator service starting up...")
    try:
        await grpc_client.connect()
    except ConnectionError as e:
        logging.critical(f"FATAL: Could not connect to gRPC services on startup: {e}")
        # In a real system, you might exit or enter a degraded state.
        # For now, we log a critical error.
    yield
    logging.info("Orchestrator service shutting down...")
    await grpc_client.close()

app = FastAPI(
    title="Sentinel AI Orchestrator",
    version="1.0.0",
    description="The AI brain of the Sentinel system, handling complex workflows.",
    lifespan=lifespan
)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """A catch-all handler for any unexpected exceptions."""
    logging.critical(f"Unhandled exception for request {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}