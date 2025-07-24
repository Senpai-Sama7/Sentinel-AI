# Rules

`core.rules` enforces hard constraints before executing an attack plan.

## Example

```python
from core.attack_tree import AttackTree
from core.rules import check_db_requires_firewall, RuleViolation

plan = AttackTree("Start")
plan.add_child("Start", "Gain_DB_Access")

try:
    check_db_requires_firewall(plan)
except RuleViolation as e:
    print("Violation:", e)
```
