from __future__ import annotations

"""Hard constraints for attack simulations or workflows."""

from graphs.knowledge_graph import KnowledgeGraph


class RuleViolation(Exception):
    """Raised when a rule check fails."""


def check_db_access(graph: KnowledgeGraph) -> None:
    """Ensure the firewall has been bypassed before DB access.

    Looks for a node named ``Firewall``. If present and its ``bypassed``
    attribute is not ``True``, access to the ``DB`` node is forbidden and a
    :class:`RuleViolation` is raised.
    """

    if "Firewall" in graph.graph and "DB" in graph.graph:
        fw = graph.graph.nodes["Firewall"]
        if not fw.get("bypassed", False):
            raise RuleViolation("No access to DB unless firewall bypassed.")


def run_pre_execution_checks(graph: KnowledgeGraph) -> None:
    """Run all rule checks against ``graph``."""

    check_db_access(graph)
