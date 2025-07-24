from __future__ import annotations

"""Attack tree structures for modeling preconditions and actions."""

from typing import Dict, Iterable
from anytree import Node, PreOrderIter
import networkx as nx

from graphs.knowledge_graph import KnowledgeGraph


class AttackTree:
    """Hierarchical attack or decision logic with cross links."""

    def __init__(self, root: str) -> None:
        self.root = Node(root)
        self._nodes: Dict[str, Node] = {root: self.root}
        self._graph = nx.DiGraph()
        self._graph.add_node(root)
        self._asset_map: Dict[str, str] = {}

    def add_child(self, parent: str, child: str) -> None:
        """Add a child node under ``parent``."""
        if parent not in self._nodes:
            raise ValueError(f"Parent '{parent}' not found")
        node = Node(child, parent=self._nodes[parent])
        self._nodes[child] = node
        self._graph.add_node(child)
        self._graph.add_edge(parent, child)

    def traverse(self) -> Iterable[str]:
        """Return a preorder listing of node names."""
        return [n.name for n in PreOrderIter(self.root)]

    def link_asset(self, node: str, asset: str) -> None:
        """Associate a tree node with an asset in the knowledge graph."""
        if node not in self._nodes:
            raise ValueError(f"Node '{node}' not found")
        self._asset_map[node] = asset

    def link_asset_from_graph(self, graph: "KnowledgeGraph", node: str, asset: str) -> None:
        """Link a tree node to an existing asset in ``graph``."""
        if asset not in graph.graph:
            raise ValueError(f"Asset '{asset}' not present in graph")
        self.link_asset(node, asset)

    def get_asset(self, node: str) -> str | None:
        """Retrieve the associated asset for a node if one exists."""
        return self._asset_map.get(node)

    def add_alternate_path(self, src: str, dst: str) -> None:
        """Add a cross-link representing an alternate attack step."""
        if src not in self._nodes or dst not in self._nodes:
            raise ValueError("Both nodes must exist in the tree")
        self._graph.add_edge(src, dst)

    def has_cycle(self) -> bool:
        """Return ``True`` if cross-links introduce a cycle."""
        try:
            nx.find_cycle(self._graph, orientation="original")
            return True
        except nx.exception.NetworkXNoCycle:
            return False

    def is_dead_end(self, node: str) -> bool:
        """Return ``True`` if ``node`` has no children."""
        if node not in self._nodes:
            raise ValueError(f"Node '{node}' not found")
        return len(self._nodes[node].children) == 0
