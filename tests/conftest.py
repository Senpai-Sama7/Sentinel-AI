# tests/conftest.py

import os
os.environ["PYTEST"] = "1"

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from fastapi.testclient import TestClient
from httpx import AsyncClient
import httpx
import pytest_asyncio

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
    mock.semantic_search = AsyncMock()
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

    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()