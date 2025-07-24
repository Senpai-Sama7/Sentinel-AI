"""Multi-agent simulation utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List
import numpy as np


@dataclass
class Agent:
    """Represents a simple agent with a position in search space."""
    name: str
    position: np.ndarray
    velocity: np.ndarray


class MultiAgentSimulator:
    """Very small Particle Swarm Optimization demonstration."""

    def __init__(self, dim: int = 2, num_agents: int = 3) -> None:
        self.dim = dim
        self.agents: List[Agent] = [
            Agent(f"agent_{i}", np.random.randn(dim), np.zeros(dim))
            for i in range(num_agents)
        ]
        self.global_best = self.agents[0].position.copy()

    def step(self) -> None:
        """Advance the simulation by one iteration."""
        for agent in self.agents:
            r = np.random.rand(self.dim)
            agent.velocity += r * (self.global_best - agent.position)
            agent.position += agent.velocity
            if np.linalg.norm(agent.position) < np.linalg.norm(self.global_best):
                self.global_best = agent.position.copy()

    def run(self, steps: int = 10) -> np.ndarray:
        """Run multiple iterations and return the best position found."""
        for _ in range(steps):
            self.step()
        return self.global_best
