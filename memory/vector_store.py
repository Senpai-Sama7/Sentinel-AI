from __future__ import annotations

"""Simple vector store client backed by Weaviate."""

from typing import Any, List, Optional
import hashlib

import numpy as np
import weaviate


class VectorStore:
    """Store and retrieve reasoning chains or attack paths as vectors."""

    def __init__(
        self,
        url: str,
        class_name: str = "ReasoningMemory",
        client: Optional[Any] = None,
    ) -> None:
        self.client = client or weaviate.Client(url)
        if not self.client.is_ready():
            raise ConnectionError("Weaviate server is not ready")
        self.class_name = class_name
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        if hasattr(self.client, "schema") and hasattr(self.client.schema, "contains"):
            if not self.client.schema.contains({"class": self.class_name}):
                schema = {
                    "classes": [
                        {
                            "class": self.class_name,
                            "vectorizer": "none",
                            "properties": [{"name": "text", "dataType": ["text"]}],
                        }
                    ]
                }
                self.client.schema.create(schema)

    @staticmethod
    def _embed(text: str) -> List[float]:
        digest = hashlib.sha256(text.encode()).digest()
        # Normalize bytes to floats for a deterministic embedding
        return [b / 255.0 for b in digest[:32]]

    def add_entry(self, text: str) -> str:
        vector = self._embed(text)
        return self.client.data_object.create(
            data_object={"text": text}, class_name=self.class_name, vector=vector
        )

    def query_similar(self, text: str, top_k: int = 3) -> List[str]:
        vector = self._embed(text)
        result = (
            self.client.query.get(self.class_name, ["text"])
            .with_near_vector({"vector": vector})
            .with_limit(top_k)
            .do()
        )
        docs = result.get("data", {}).get("Get", {}).get(self.class_name, [])
        return [d["text"] for d in docs]
