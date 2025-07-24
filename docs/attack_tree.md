# Attack Trees

`AttackTree` models prerequisite actions as a hierarchy that can reference assets in the knowledge graph.

## Basic Usage

```python
from core.attack_tree import AttackTree

# create the tree
tree = AttackTree("Gain_DB_Access")
tree.add_child("Gain_DB_Access", "Exploit_Firewall")
tree.add_child("Gain_DB_Access", "Phish_Admin")
```

Nodes may link to assets or connections stored in the knowledge graph:

```python
from graphs.knowledge_graph import KnowledgeGraph

net = KnowledgeGraph()
net.add_asset("Server_B")

tree.add_child("Exploit_Firewall", "Exploit_Server_B")
tree.link_asset("Exploit_Server_B", "Server_B")
```

Alternate attack paths can be represented with cross-links and cycles are detected automatically:

```python
# create a shortcut from phishing to exploiting the firewall
tree.add_alternate_path("Phish_Admin", "Exploit_Firewall")
if tree.has_cycle():
    print("cycle detected")
```

## Advanced

Check for dead ends when traversing a tree:

```python
leaf = "Exploit_Server_B"
print(tree.is_dead_end(leaf))  # True when no further actions are defined
```
