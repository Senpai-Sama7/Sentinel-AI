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
