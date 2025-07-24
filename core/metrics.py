import os
from prometheus_client import Counter, CollectorRegistry, multiprocess

registry = CollectorRegistry()
if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
    multiprocess.MultiProcessCollector(registry)

documents_ingested_total = Counter(
    "documents_ingested_total", "Total documents ingested", registry=registry
)
