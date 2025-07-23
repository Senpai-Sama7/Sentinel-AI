import networkx as nx
from typing import Any, Iterable, List

class KnowledgeGraph:
    """Simple wrapper around networkx.DiGraph for asset relationships."""

    def __init__(self) -> None:
        self.graph = nx.DiGraph()

    def add_asset(self, name: str, **attrs: Any) -> None:
        """Add a node representing an asset or entity."""
        self.graph.add_node(name, **attrs)

    def add_connection(self, src: str, dst: str, **attrs: Any) -> None:
        """Add a directed edge between two assets."""
        self.graph.add_edge(src, dst, **attrs)

    def paths(self, source: str, target: str) -> List[List[str]]:
        """Return all simple paths between two assets."""
        return list(nx.all_simple_paths(self.graph, source, target))

    def neighbors(self, node: str) -> Iterable[str]:
        """Return neighbors of a given asset."""
        return self.graph.neighbors(node)
