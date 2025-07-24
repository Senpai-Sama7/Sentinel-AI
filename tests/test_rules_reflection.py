from core.attack_tree import AttackTree
from core.rules import check_db_requires_firewall, RuleViolation
from core.reflection import reflect
import pytest


def test_firewall_rule():
    tree = AttackTree("Start")
    tree.add_child("Start", "Gain_DB_Access")
    with pytest.raises(RuleViolation):
        check_db_requires_firewall(tree)
    tree.add_child("Start", "Exploit_Firewall")
    check_db_requires_firewall(tree)


def test_reflection_output(caplog):
    message = reflect("success", "penetrated target")
    assert "Lesson learned" in message
    assert "success" in message

