import networkx as nx
from typing import Any, Iterable, List, Dict

class KnowledgeGraph:
    """Wrapper around networkx graphs for modeling asset relationships."""

    def __init__(self, directed: bool = True) -> None:
        """Initialize the graph.

        Parameters
        ----------
        directed:
            If ``True`` (default) a :class:`~networkx.DiGraph` is used.
            Otherwise a standard undirected graph is created.
        """
        self.graph = nx.DiGraph() if directed else nx.Graph()

    def add_asset(self, name: str, **attrs: Any) -> None:
        """Add a node representing an asset or entity with attributes."""
        self.graph.add_node(name, **attrs)

    def get_asset_attrs(self, name: str) -> Dict[str, Any]:
        """Return the attribute dictionary for a given asset."""
        return dict(self.graph.nodes[name])

    def add_connection(self, src: str, dst: str, weight: float = 1.0, **attrs: Any) -> None:
        """Add an edge between two assets.

        Parameters
        ----------
        src, dst:
            Source and destination asset names.
        weight:
            Numeric edge weight used for path scoring (default ``1.0``).
        attrs:
            Additional edge attributes such as ``type`` or ``risk``.
        """
        attrs.setdefault("weight", weight)
        self.graph.add_edge(src, dst, **attrs)

    def add_directed_connection(self, src: str, dst: str, weight: float = 1.0, **attrs: Any) -> None:
        """Explicitly add a directed edge even when using an undirected graph."""
        attrs.setdefault("weight", weight)
        if isinstance(self.graph, nx.DiGraph):
            self.graph.add_edge(src, dst, **attrs)
        else:
            self.graph.add_edge(src, dst, **attrs)

    def get_connection_attrs(self, src: str, dst: str) -> Dict[str, Any]:
        """Return attribute dictionary for a connection."""
        data = self.graph.get_edge_data(src, dst)
        return dict(data) if data else {}

    def paths(self, source: str, target: str) -> List[List[str]]:
        """Return all simple paths between two assets."""
        return list(nx.all_simple_paths(self.graph, source, target))

    def shortest_path(self, source: str, target: str, weight: str = "weight") -> List[str]:
        """Return the weighted shortest path between two assets."""
        return nx.shortest_path(self.graph, source, target, weight=weight)

    def neighbors(self, node: str) -> Iterable[str]:
        """Return neighbors of a given asset."""
        return self.graph.neighbors(node)
