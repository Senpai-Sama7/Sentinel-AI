# Reasoning Engine

The reasoning engine parses step-by-step answers from the LLM and stores them as structured data. Each step becomes a node in a small tree so alternate branches can be explored later.

```python
from core.reasoning import parse_reasoning_steps, ReasoningTree

text = "1. Scan open ports\n2. Exploit service\nFinished."
steps = parse_reasoning_steps(text)

rtree = ReasoningTree("analysis")
rtree.add_branches("root", steps)
print(rtree.traverse())
```
