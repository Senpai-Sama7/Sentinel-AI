# main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from api.routes import router
from api.dependencies import memory_manager
from core.config import LOG_LEVEL
from core.logging import setup_logging
from core.exceptions import MemoryLayerError, NotFoundError

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's startup and shutdown events using an async context manager.
    This is the recommended approach for modern FastAPI applications.
    """
    # --- Startup ---
    setup_logging(LOG_LEVEL)
    logging.info("Application startup sequence initiated.")
    try:
        if memory_manager is not None:
            await memory_manager.startup()
    except MemoryLayerError as e:
        logging.critical(f"A critical memory layer failed to start: {e}. Shutting down.")
        # In a real K8s environment, this failure would cause the pod to crash-loop,
        # signaling a configuration or dependency issue.
        raise e
    
    yield  # The application runs while the context manager is active
    
    # --- Shutdown ---
    logging.info("Application shutdown sequence initiated.")
    if memory_manager is not None:
        await memory_manager.shutdown()

app = FastAPI(
    title="Sentinel AI Memory Service",
    version="1.0.0",
    description="A production-grade, multi-layered memory system for AI agents.",
    lifespan=lifespan
)

# --- Global Exception Handlers ---
# These handlers ensure that the API always returns a clean, structured JSON
# error response, preventing stack traces from leaking to the client.

@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    """Handles errors for resources not found in any memory layer."""
    logging.warning(f"Resource not found for request {request.url.path}: {exc}")
    return JSONResponse(
        status_code=404,
        content={"message": str(exc)},
    )

@app.exception_handler(MemoryLayerError)
async def memory_layer_exception_handler(request: Request, exc: MemoryLayerError):
    """Handles errors when a backend service (Redis, Weaviate, etc.) is unavailable."""
    logging.error(f"Memory layer failure during request to {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=503,  # Service Unavailable
        content={"message": f"A required memory service is unavailable: {exc}"},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """A catch-all handler for any other unexpected exceptions."""
    logging.critical(f"An unhandled exception occurred for request {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected internal server error occurred."},
    )

# Include the API router with a versioned prefix
app.include_router(router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
async def health_check():
    """Provides a simple health check endpoint."""
    # In a real system, this would check connections to Redis, Weaviate, etc.
    return {"status": "ok", "message": "Sentinel AI Memory Service is running."}
