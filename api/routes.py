# api/routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.responses import PlainTextResponse
from typing import Optional
import logging

from .dependencies import get_memory_manager
from .models import *
from core.manager import MemoryManager
from core.utils import validate_file_path, validate_commit_hash

# Create a new router instance. This helps in organizing endpoints and can be
# included in the main FastAPI app with a prefix.
router = APIRouter(prefix="/memory", tags=["Memory Operations"])


@router.get(
    "/file/{file_path:path}",
    response_model=str,
    response_class=PlainTextResponse,
    summary="Retrieve File Content",
    description="Fetches the content of a file from the memory system, using the full L0 -> L1 -> L3 (Git) fallback logic. This is the primary endpoint for retrieving source-of-truth data.",
)
async def get_file_from_memory(
    file_path: str = Path(
        ...,
        description="The full path to the file within the configured Git repository.",
        examples={"default": {"summary": "Sample file", "value": "src/main.py"}},
    ),
    commit_hash: Optional[str] = None,
    manager: MemoryManager = Depends(get_memory_manager),
):
    logging.info(
        f"API request for file: {file_path} at commit: {commit_hash or 'latest'}"
    )

    try:
        file_path = validate_file_path(file_path)
        if commit_hash is not None:
            commit_hash = validate_commit_hash(commit_hash)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

    # The actual logic is delegated entirely to the MemoryManager.
    # The API layer is only responsible for handling HTTP concerns.
    # Exceptions raised by the manager will be caught by the handlers in main.py.
    return await manager.get_file_content(file_path, commit_hash)


@router.post(
    "/search",
    response_model=SemanticSearchResponse,
    summary="Perform Semantic Search",
    description="Performs a semantic search against the L2 (ChromaDB) memory layer to find relevant documents (e.g., READMEs, docstrings) based on a natural language query.",
)
async def search_semantic_memory(
    request: SemanticSearchRequest, manager: MemoryManager = Depends(get_memory_manager)
):
    logging.info(f"API performing semantic search for query: '{request.query}'")
    results = await manager.semantic_search(request.query, request.top_k)
    # The response from ChromaDB already matches the desired structure.
    return results


@router.post(
    "/cache",
    response_model=SetMemoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Set a Cache Item",
    description="Sets a value in the cache (L0/L1) and optionally persists it to the L2 (Weaviate) layer for long-term structured storage. Useful for storing computed results from AI analysis.",
)
async def set_memory_item(
    request: SetMemoryRequest, manager: MemoryManager = Depends(get_memory_manager)
):
    logging.info(f"API setting memory for key: {request.key}")
    if request.persist_to_l2:
        # This demonstrates calling the persistence logic
        await manager.persist_node(
            "MemoryNode", {"key": request.key, "value": request.value}
        )
        message = f"Successfully set key '{request.key}' in cache and persisted to L2."
    else:
        # This demonstrates calling the cache-only logic
        await manager.set_cache_item(request.key, request.value)
        message = f"Successfully set key '{request.key}' in L0/L1 cache."

    return SetMemoryResponse(key=request.key, status="success", message=message)
