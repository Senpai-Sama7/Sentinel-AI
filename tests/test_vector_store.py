from memory.vector_store import VectorStore
import numpy as np
from types import SimpleNamespace


class FakeQuery:
    def __init__(self, store, class_name):
        self.store = store
        self.class_name = class_name
        self.vector = []
        self.limit = 0

    def get(self, class_name, props):
        self.class_name = class_name
        return self

    def with_near_vector(self, near):
        self.vector = near["vector"]
        return self

    def with_limit(self, k):
        self.limit = k
        return self

    def do(self):
        sims = []
        for item in self.store:
            v = np.array(item["vector"])
            q = np.array(self.vector)
            s = float(v.dot(q) / (np.linalg.norm(v) * np.linalg.norm(q)))
            sims.append((s, item["text"]))
        sims.sort(reverse=True)
        data = [{"text": t} for _, t in sims[: self.limit]]
        return {"data": {"Get": {self.class_name: data}}}


class FakeClient:
    def __init__(self):
        self.store = []
        self.schema = SimpleNamespace(contains=lambda x: True, create=lambda x: None)
        self.data_object = SimpleNamespace(create=self._create)
        self.query = SimpleNamespace(get=self._get)

    def _create(self, data_object, class_name, vector):
        self.store.append({"text": data_object["text"], "vector": vector})
        return str(len(self.store))

    def _get(self, class_name, props):
        return FakeQuery(self.store, class_name)

    def is_ready(self):
        return True


def test_add_and_query(monkeypatch):
    fake_client = FakeClient()
    store = VectorStore(url="http://test", client=fake_client)
    store.add_entry("compromise server")
    store.add_entry("backup data")
    results = store.query_similar("compromise server", top_k=1)
    assert results == ["compromise server"]
