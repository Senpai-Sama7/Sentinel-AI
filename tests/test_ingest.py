import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_ingest_and_search(async_test_app_client: AsyncClient, mock_memory_manager: AsyncMock):
    mock_memory_manager.ingest_document = AsyncMock()
    mock_memory_manager.semantic_search = AsyncMock(return_value={
        "ids": [["hello.txt"]],
        "documents": [["hello ingestion world"]],
        "metadatas": [[{"source": "hello.txt"}]],
        "distances": [[0.01]]
    })

    response = await async_test_app_client.post(
        "/api/v1/memory/ingest",
        files={"file": ("hello.txt", b"hello ingestion world")}
    )
    assert response.status_code == 200
    mock_memory_manager.ingest_document.assert_awaited_once()

    search = await async_test_app_client.post(
        "/api/v1/memory/search",
        json={"query": "ingestion", "top_k": 1}
    )
    assert search.status_code == 200
    assert search.json()["documents"][0][0] == "hello ingestion world"


@pytest.mark.asyncio
async def test_ingest_empty_file(async_test_app_client: AsyncClient, mock_memory_manager: AsyncMock):
    response = await async_test_app_client.post(
        "/api/v1/memory/ingest",
        files={"file": ("empty.txt", b"")}
    )
    assert response.status_code == 400
