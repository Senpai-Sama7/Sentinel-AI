from core.reasoning import parse_reasoning_steps, ReasoningTree


def test_parse_reasoning_steps():
    text = "1. Step one\n2. Step two\nFinal answer."
    steps = parse_reasoning_steps(text)
    assert steps == ["Step one", "Step two"]


def test_reasoning_tree_traversal():
    tree = ReasoningTree("start")
    tree.add_branches("root", ["A", "B"])
    assert tree.traverse() == ["start", "A", "B"]
