# Symbolic Rules & Reflection

These modules provide a basic framework for enforcing hard constraints and logging lessons learned after each run.

## Rule Checks

```python
from graphs.knowledge_graph import KnowledgeGraph
from core.rules import run_pre_execution_checks, RuleViolation

net = KnowledgeGraph()
net.add_asset("Firewall")
net.add_asset("DB")

# raises RuleViolation until firewall is marked bypassed
try:
    run_pre_execution_checks(net)
except RuleViolation:
    net.graph.nodes["Firewall"]["bypassed"] = True
    run_pre_execution_checks(net)
```

## Reflection

```python
from core.reflection import reflect

lesson = reflect("simulation success")
print(lesson)
```

Call `reflect()` after each attack simulation or agent action to capture the outcome and generate a brief lesson learned.
