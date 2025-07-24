from __future__ import annotations

"""Reasoning utilities for Chain/Tree/Graph-of-Thought."""

from typing import List
import re
from anytree import Node, PreOrderIter
import networkx as nx


def parse_reasoning_steps(text: str) -> List[str]:
    """Extract reasoning steps from an LLM answer."""
    steps: List[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^\d+[\.)]\s*(.*)", line)
        if m:
            steps.append(m.group(1))
            continue
        if line.startswith("- "):
            steps.append(line[2:])
            continue
    if not steps and text.strip():
        steps.append(text.strip())
    return steps


class ReasoningTree:
    """Simple container for branching reasoning paths."""

    def __init__(self, root_text: str) -> None:
        self.root = Node("root", text=root_text)
        self._nodes = {"root": self.root}
        self._graph = nx.DiGraph()
        self._graph.add_node("root", text=root_text)
        self._counter = 0

    def add_branches(self, parent: str, branches: List[str]) -> List[str]:
        if parent not in self._nodes:
            raise ValueError(f"Parent '{parent}' not found")
        ids: List[str] = []
        for text in branches:
            self._counter += 1
            node_id = f"n{self._counter}"
            node = Node(node_id, parent=self._nodes[parent], text=text)
            self._nodes[node_id] = node
            self._graph.add_node(node_id, text=text)
            self._graph.add_edge(parent, node_id)
            ids.append(node_id)
        return ids

    def traverse(self) -> List[str]:
        """Return preorder list of node texts."""
        return [n.text for n in PreOrderIter(self.root)]
