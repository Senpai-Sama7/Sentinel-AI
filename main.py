# main.py

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from contextlib import asynccontextmanager
import logging
import os

from api.routes import router
from api.advanced_routes import router as advanced_router
from api.dependencies import get_memory_manager
from core.metrics import registry, documents_ingested_total
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
    if os.getenv("PYTEST"):
        manager = None
    else:
        manager = await get_memory_manager()
        try:
            await manager.startup()
        except MemoryLayerError as e:
            logging.critical(
                f"A critical memory layer failed to start: {e}. Shutting down."
            )
            raise e


app = FastAPI(
    title="Sentinel AI Memory Service",
    version="1.0.0",
    description="A production-grade, multi-layered memory system for AI agents.",
    lifespan=lifespan,
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
    logging.error(
        f"Memory layer failure during request to {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=503,  # Service Unavailable
        content={"message": f"A required memory service is unavailable: {exc}"},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """A catch-all handler for any other unexpected exceptions."""
    logging.critical(
        f"An unhandled exception occurred for request {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected internal server error occurred."},
    )


# Include the API router with a versioned prefix
app.include_router(router)
app.include_router(advanced_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Checks connectivity to Redis and ChromaDB."""
    manager = await get_memory_manager()
    redis_ok, chroma_ok = True, True
    try:
        await manager.l1.pool.ping()
    except Exception as e:
        logging.error(f"Redis health check failed: {e}")
        redis_ok = False
    try:
        manager.l2c.client.heartbeat()
    except Exception as e:
        logging.error(f"ChromaDB health check failed: {e}")
        chroma_ok = False
    status = "ok" if redis_ok and chroma_ok else "degraded"
    return {"status": status, "redis": redis_ok, "chroma": chroma_ok}


@app.get("/metrics")
async def metrics() -> Response:
    """Exposes Prometheus metrics."""
    data = generate_latest(registry)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
