from core.attack_tree import AttackTree
from graphs.knowledge_graph import KnowledgeGraph


def test_tree_traversal():
    tree = AttackTree("Gain_DB_Access")
    tree.add_child("Gain_DB_Access", "Exploit_Firewall")
    tree.add_child("Gain_DB_Access", "Phish_Admin")
    assert tree.traverse()[:3] == ["Gain_DB_Access", "Exploit_Firewall", "Phish_Admin"]


def test_mapping_and_cycle_detection():
    graph = KnowledgeGraph()
    graph.add_asset("Server_B")

    tree = AttackTree("Root")
    tree.add_child("Root", "Exploit_Server_B")
    tree.link_asset("Exploit_Server_B", "Server_B")

    assert tree.get_asset("Exploit_Server_B") == "Server_B"
    assert not tree.has_cycle()

    tree.add_alternate_path("Exploit_Server_B", "Root")
    assert tree.has_cycle()


def test_dead_end_detection():
    tree = AttackTree("Root")
    tree.add_child("Root", "Step1")
    tree.add_child("Step1", "Leaf")

    assert tree.is_dead_end("Leaf")
    assert not tree.is_dead_end("Step1")
