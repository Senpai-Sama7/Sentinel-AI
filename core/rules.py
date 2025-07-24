"""Hard rule enforcement for attack plans."""

from __future__ import annotations

from core.attack_tree import AttackTree


class RuleViolation(Exception):
    """Raised when a plan violates a hard constraint."""


def check_db_requires_firewall(tree: AttackTree) -> None:
    """Raise :class:`RuleViolation` if DB access occurs without firewall bypass."""
    steps = tree.traverse()
    if "Gain_DB_Access" in steps and "Exploit_Firewall" not in steps:
        raise RuleViolation("No access to DB unless firewall bypassed")


def run_all(tree: AttackTree) -> None:
    """Run all built-in rule checks on ``tree``."""
    check_db_requires_firewall(tree)
