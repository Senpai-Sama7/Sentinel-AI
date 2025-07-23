# Knowledge Graph

Sentinel AI includes a lightweight wrapper around `networkx` for representing assets and their relationships.
Nodes and edges accept arbitrary attributes so you can capture properties like operating system, credentials,
vulnerabilities or connection risk.

## Basic Usage

```python
from graphs.knowledge_graph import KnowledgeGraph

net = KnowledgeGraph()
net.add_asset("Server_A", os="Ubuntu", vulnerabilities=["CVE-2023-1234"])
net.add_asset("DB", sensitive=True)
net.add_connection("Server_A", "DB", type="sql", risk=8, weight=0.5)

print(net.get_asset_attrs("Server_A"))
print(net.get_connection_attrs("Server_A", "DB"))
path = net.shortest_path("Server_A", "DB")
print(path)
```

`shortest_path` uses edge weights when present to calculate the lowest-cost route.
