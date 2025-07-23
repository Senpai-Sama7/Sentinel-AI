# tests/test_api.py

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
import os

# Ensure required environment variables are set for tests
REQUIRED_ENV_VARS = [
    "JWT_SECRET",
    "OPENAI_API_KEY",
    "REDIS_URL",
    "CHROMA_HOST",
    "CHROMA_PORT",
    "APP_CORS_ORIGINS",
    "LOG_LEVEL",
    "WEAVIATE_URL",
    "GIT_REPO_PATH",
    "L0_CACHE_SIZE",
    "GO_PROXY_GRPC_ADDR",
    "CHROMA_DB_PATH",
]
for _var in REQUIRED_ENV_VARS:
    os.environ.setdefault(_var, "test")

from core.exceptions import NotFoundError, MemoryLayerError

# Mark all tests in this file as requiring an asyncio event loop
# pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_health_check(async_test_app_client: AsyncClient):
    """Tests that the health check endpoint is available and returns success."""
    response = await async_test_app_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Sentinel AI Memory Service is running."}

@pytest.mark.asyncio
async def test_get_file_success(async_test_app_client: AsyncClient, mock_memory_manager: AsyncMock):
    """Tests the successful retrieval of a file."""
    file_path = "src/main.py"
    file_content = "print('hello world')"
    mock_memory_manager.get_file_content.return_value = file_content

    response = await async_test_app_client.get(f"/memory/file/{file_path}")

    assert response.status_code == 200
    assert response.text == file_content
    # Verify that the manager was called with the correct arguments
    mock_memory_manager.get_file_content.assert_called_once_with(file_path, None)

@pytest.mark.asyncio
async def test_get_file_not_found(async_test_app_client: AsyncClient, mock_memory_manager: AsyncMock):
    """Tests the 404 response when a file is not found in any layer."""
    file_path = "non/existent/file.py"
    # Configure the mock to raise the specific exception our app handles
    mock_memory_manager.get_file_content.side_effect = NotFoundError(f"File '{file_path}' not found.")

    response = await async_test_app_client.get(f"/memory/file/{file_path}")

    assert response.status_code == 404
    assert response.json() == {"message": f"File '{file_path}' not found."}

@pytest.mark.asyncio
async def test_get_file_memory_layer_failure(async_test_app_client: AsyncClient, mock_memory_manager: AsyncMock):
    """Tests the 503 response when a backend service is unavailable."""
    file_path = "src/main.py"
    # Configure the mock to raise a service error
    mock_memory_manager.get_file_content.side_effect = MemoryLayerError("L3-Git", "Repository is corrupted.")

    response = await async_test_app_client.get(f"/memory/file/{file_path}")

    assert response.status_code == 503
    assert "A required memory service is unavailable" in response.json()["message"]
    assert "[L3-Git] Repository is corrupted" in response.json()["message"]

@pytest.mark.asyncio
async def test_semantic_search_success(async_test_app_client: AsyncClient, mock_memory_manager: AsyncMock):
    """Tests the semantic search endpoint."""
    mock_response = {
        "ids": [["doc1"]],
        "documents": [["This is a test document."]],
        "metadatas": [[{"source": "README.md"}]],
        "distances": [[0.123]]
    }
    mock_memory_manager.semantic_search.return_value = mock_response
    
    request_data = {"query": "test query", "top_k": 1}
    response = await async_test_app_client.post("/memory/search", json=request_data)

    assert response.status_code == 200
    assert response.json()["documents"][0][0] == "This is a test document."

def test_required_env_vars_present():
    required_vars = [
        "JWT_SECRET",
        "OPENAI_API_KEY",
        "REDIS_URL",
        "CHROMA_HOST",
        "CHROMA_PORT",
        "APP_CORS_ORIGINS",
        "LOG_LEVEL",
        "WEAVIATE_URL",
        "GIT_REPO_PATH",
        "L0_CACHE_SIZE",
        "GO_PROXY_GRPC_ADDR",
        "CHROMA_DB_PATH",
    ]
    missing = [var for var in required_vars if not os.getenv(var)]
    assert not missing, f"Missing required env vars: {missing}"

