"""Additional API endpoints exposing advanced modules."""
from fastapi import APIRouter
from typing import List

from api.models import (
    TemporalLogResponse,
    ClusterResponse,
    AgentRunResponse,
    FuseResponse,
)

from advanced.temporal_module import TemporalSequenceLogger
from advanced.topology_module import TopologicalAnalyzer
from advanced.multiagent_module import MultiAgentSimulator
from advanced.fusion_module import MultiModalFusion
from advanced.personalization import UserProfileManager
from advanced.continuous_learning import OnlineTrainer


router = APIRouter(prefix="/advanced", tags=["Advanced"])

logger = TemporalSequenceLogger()
tda = TopologicalAnalyzer()
simulator = MultiAgentSimulator()
fuser = MultiModalFusion()
profiles = UserProfileManager()
trainer = OnlineTrainer()


@router.post("/temporal/{user_id}", response_model=TemporalLogResponse)
async def log_action(user_id: str, action: str) -> TemporalLogResponse:
    logger.log_action(user_id, action)
    return TemporalLogResponse(sequence=logger.get_sequence(user_id))


@router.get("/topology/cluster", response_model=ClusterResponse)
async def topology_cluster() -> ClusterResponse:
    import numpy as np
    vectors = np.random.rand(5, 3)
    labels = tda.cluster_embeddings(vectors)
    if hasattr(labels, "tolist"):
        labels = labels.tolist()
    return ClusterResponse(labels=labels)


@router.post("/agents/run", response_model=AgentRunResponse)
async def run_agents(steps: int = 5) -> AgentRunResponse:
    best = simulator.run(steps)
    return AgentRunResponse(best_position=best.tolist())


@router.post("/fuse", response_model=FuseResponse)
async def fuse_vectors() -> FuseResponse:
    import numpy as np
    fused = fuser.fuse(np.ones(2), np.zeros(2))
    return FuseResponse(vector=fused.tolist())


@router.post("/profile/{user_id}")
async def update_profile(user_id: str, data: dict):
    profiles.update_profile(user_id, data)
    return profiles.get_profile(user_id)


@router.post("/learn")
async def online_learn(data: dict):
    trainer.update(data)
    trainer.train()
    return {"status": "updated"}
