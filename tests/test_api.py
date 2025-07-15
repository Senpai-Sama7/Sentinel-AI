# tests/test_api.py

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock

from core.exceptions import NotFoundError, MemoryLayerError

# Mark all tests in this file as requiring an asyncio event loop
pytestmark = pytest.mark.asyncio

async def test_health_check(async_test_app_client: AsyncClient):
    """Tests that the health check endpoint is available and returns success."""
    response = await async_test_app_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Sentinel AI Memory Service is running."}

async def test_get_file_success(async_test_app_client: AsyncClient, mock_memory_manager: AsyncMock):
    """Tests the successful retrieval of a file."""
    file_path = "src/main.py"
    file_content = "print('hello world')"
    mock_memory_manager.get_file_content.return_value = file_content

    response = await async_test_app_client.get(f"/api/v1/file/{file_path}")

    assert response.status_code == 200
    assert response.json() == file_content
    # Verify that the manager was called with the correct arguments
    mock_memory_manager.get_file_content.assert_called_once_with(file_path, None)

async def test_get_file_not_found(async_test_app_client: AsyncClient, mock_memory_manager: AsyncMock):
    """Tests the 404 response when a file is not found in any layer."""
    file_path = "non/existent/file.py"
    # Configure the mock to raise the specific exception our app handles
    mock_memory_manager.get_file_content.side_effect = NotFoundError(f"File '{file_path}' not found.")

    response = await async_test_app_client.get(f"/api/v1/file/{file_path}")

    assert response.status_code == 404
    assert response.json() == {"message": f"File '{file_path}' not found."}

async def test_get_file_memory_layer_failure(async_test_app_client: AsyncClient, mock_memory_manager: AsyncMock):
    """Tests the 503 response when a backend service is unavailable."""
    file_path = "src/main.py"
    # Configure the mock to raise a service error
    mock_memory_manager.get_file_content.side_effect = MemoryLayerError("L3-Git", "Repository is corrupted.")

    response = await async_test_app_client.get(f"/api/v1/file/{file_path}")

    assert response.status_code == 503
    assert "A required memory service is unavailable" in response.json()["message"]
    assert "[L3-Git] Repository is corrupted" in response.json()["message"]

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
    response = await async_test_app_client.post("/api/v1/search", json=request_data)

    assert response.status_code == 200
    assert response.json()["documents"][0][0] == "This is a test document."
    mock_memory_manager.semantic_search.assert_awaited_once_with("test query", 1)


async def test_set_cache_no_persist(async_test_app_client: AsyncClient, mock_memory_manager: AsyncMock):
    """Tests setting a cache item without persisting to L2."""
    request_data = {"key": "test", "value": "val", "persist_to_l2": False}

    response = await async_test_app_client.post("/api/v1/cache", json=request_data)

    assert response.status_code == 201
    assert response.json()["message"] == "Successfully set key 'test' in L0/L1 cache."
    mock_memory_manager.set_cache_item.assert_awaited_once_with("test", "val")
    mock_memory_manager.persist_node.assert_not_called()


async def test_set_cache_with_persist(async_test_app_client: AsyncClient, mock_memory_manager: AsyncMock):
    """Tests setting a cache item and persisting it to L2."""
    request_data = {"key": "test2", "value": "val2", "persist_to_l2": True}

    response = await async_test_app_client.post("/api/v1/cache", json=request_data)

    assert response.status_code == 201
    assert response.json()["message"] == "Successfully set key 'test2' in cache and persisted to L2."
    mock_memory_manager.persist_node.assert_awaited_once_with("MemoryNode", {"key": "test2", "value": "val2"})
    mock_memory_manager.set_cache_item.assert_not_called()
