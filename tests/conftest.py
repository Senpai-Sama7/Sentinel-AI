# tests/conftest.py

import os
os.environ["PYTEST"] = "1"

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import MagicMock, AsyncMock
import weaviate
import git
import redis.asyncio as redis

# Patch the Weaviate client to avoid real network calls during import
weaviate.Client = MagicMock(return_value=MagicMock(is_ready=lambda: True))
git.Repo = MagicMock(return_value=MagicMock(is_dirty=lambda *a, **k: False, head=MagicMock(commit=MagicMock(hexsha="0"*40))))
redis.from_url = AsyncMock(return_value=AsyncMock(ping=AsyncMock()))

from fastapi.testclient import TestClient

# Import the main app object and the dependency getters we want to override
from main import app
from api.dependencies import get_memory_manager
from core.manager import MemoryManager

@pytest.fixture(scope="session")
def event_loop():
    """Creates a new asyncio event loop for the entire test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_memory_manager() -> MagicMock:
    """
    A pytest fixture that creates a mock of the MemoryManager.
    This allows us to control its behavior during tests without touching real databases.
    """
    mock = MagicMock(spec=MemoryManager)
    # Configure the async methods with AsyncMock
    mock.get_file_content = AsyncMock()
    async def _semantic_search(query: str, top_k: int = 5):
        return await mock.l2c.query(query, top_k)

    mock.semantic_search = AsyncMock(side_effect=_semantic_search)
    mock.set_cache_item = AsyncMock()
    mock.persist_node = AsyncMock()
    mock.l2c = MagicMock()
    mock.l2c.query = AsyncMock()
    return mock

@pytest.fixture
def test_app_client(mock_memory_manager: MagicMock) -> TestClient:
    """
    Creates a FastAPI TestClient with the MemoryManager dependency overridden.
    This is useful for testing synchronous parts of the API if any.
    """
    # Override the dependency: when get_memory_manager is called, return our mock instead.
    app.dependency_overrides[get_memory_manager] = lambda: mock_memory_manager
    # Replace the global memory_manager used by lifespan events
    from api import dependencies
    dependencies.memory_manager = mock_memory_manager
    import main as main_module
    main_module.memory_manager = mock_memory_manager
    
    with TestClient(app) as client:
        yield client
    
    # Clean up the override after the test is done
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def async_test_app_client(mock_memory_manager: MagicMock) -> AsyncClient:
    """
    Creates an httpx.AsyncClient for testing async endpoints. This is the
    preferred client for testing an asyncio-based application.
    """
    app.dependency_overrides[get_memory_manager] = lambda: mock_memory_manager
    from api import dependencies
    dependencies.memory_manager = mock_memory_manager
    import main as main_module
    main_module.memory_manager = mock_memory_manager


    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

