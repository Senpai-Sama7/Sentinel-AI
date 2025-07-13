# orchestrator/core/rag.py
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Optional

from orchestrator.core.config import CHROMA_DB_PATH

class RAGSystem:
    """Handles Retrieval-Augmented Generation using ChromaDB and SentenceTransformers."""
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="project_documentation",
            # The embedding function can be specified here if not using default
        )

    async def add_document(self, doc_id: str, content: str, metadata: dict):
        self.collection.upsert(ids=[doc_id], documents=[content], metadatas=[metadata])

    async def query(self, query_text: str, n_results: int = 3) -> Optional[str]:
        results = self.collection.query(query_texts=[query_text], n_results=n_results)
        
        if not results or not results.get("documents"):
            return None
        
        context_lines = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            context_lines.append(f"Source: {meta.get('source', 'N/A')}\nContent: {doc}")
        
        return "\n---\n".join(context_lines)