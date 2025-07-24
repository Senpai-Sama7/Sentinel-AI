import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_temporal_logging(async_test_app_client: AsyncClient):
    resp = await async_test_app_client.post("/advanced/temporal/user1", params={"action": "edit"})
    assert resp.status_code == 200
    data = resp.json()
    assert "sequence" in data


@pytest.mark.asyncio
async def test_topology_cluster(async_test_app_client: AsyncClient):
    resp = await async_test_app_client.get("/advanced/topology/cluster")
    assert resp.status_code == 200
    assert "labels" in resp.json()


@pytest.mark.asyncio
async def test_agent_run(async_test_app_client: AsyncClient):
    resp = await async_test_app_client.post("/advanced/agents/run")
    assert resp.status_code == 200
    assert "best_position" in resp.json()
