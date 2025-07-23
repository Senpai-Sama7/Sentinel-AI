from graphs.knowledge_graph import KnowledgeGraph


def test_path_generation():
    graph = KnowledgeGraph()
    graph.add_asset("A")
    graph.add_asset("B")
    graph.add_asset("C")
    graph.add_connection("A", "B")
    graph.add_connection("B", "C")
    paths = graph.paths("A", "C")
    assert paths == [["A", "B", "C"]]


def test_attributes_and_weights():
    graph = KnowledgeGraph()
    graph.add_asset("Server_A", os="Ubuntu", vulnerabilities=["CVE-2023-1234"])
    graph.add_asset("DB")
    graph.add_connection("Server_A", "DB", type="sql", risk=8, weight=2)

    assert graph.get_asset_attrs("Server_A")["os"] == "Ubuntu"
    edge_attrs = graph.get_connection_attrs("Server_A", "DB")
    assert edge_attrs["risk"] == 8
    assert edge_attrs["weight"] == 2


def test_weighted_shortest_path():
    graph = KnowledgeGraph()
    graph.add_asset("A")
    graph.add_asset("B")
    graph.add_asset("C")
    graph.add_connection("A", "B", weight=5)
    graph.add_connection("A", "C", weight=1)
    graph.add_connection("C", "B", weight=1)

    assert graph.shortest_path("A", "B") == ["A", "C", "B"]
