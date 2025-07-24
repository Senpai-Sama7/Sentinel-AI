from core.rules import run_pre_execution_checks, RuleViolation
from core.reflection import reflect
from graphs.knowledge_graph import KnowledgeGraph


def test_rule_violation_and_pass():
    graph = KnowledgeGraph()
    graph.add_asset("Firewall")
    graph.add_asset("DB")

    # Should raise until firewall bypassed
    try:
        run_pre_execution_checks(graph)
    except RuleViolation:
        graph.graph.nodes["Firewall"]["bypassed"] = True
        run_pre_execution_checks(graph)


def test_reflection(tmp_path):
    log_file = tmp_path / "log.txt"
    lesson = reflect("operation success", log_file=str(log_file))
    assert "success" in lesson.lower()
    content = log_file.read_text()
    assert "operation success" in content
