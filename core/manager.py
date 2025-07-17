# core/manager.py

import asyncio
import json
from typing import Any, Optional, Dict, List
import logging
import hashlib

from .l0_cache import L0Cache
from .l1_redis import L1Redis
from .l2_weaviate import L2Weaviate
from .l2_chroma import L2Chroma
from .l3_git import L3Git
from .config import L0_CACHE_SIZE, REDIS_URL, WEAVIATE_URL, CHROMA_PATH, GIT_REPO_PATH
from .exceptions import MemoryLayerError, NotFoundError

class MemoryManager:
    """
    Unified memory manager orchestrating L0-L3 layers.
    This is the core orchestrator of the system, designed for high performance,
    resilience, and concurrency safety.
    """

    def __init__(self):
        """Initializes all memory layer clients and concurrency controls."""
        self.l0 = L0Cache(L0_CACHE_SIZE)
        self.l1 = L1Redis(REDIS_URL)
        self.l2w = L2Weaviate(WEAVIATE_URL)
        self.l2c = L2Chroma(CHROMA_PATH)
        self.l3 = L3Git(GIT_REPO_PATH)

        # The _locks dictionary holds an asyncio.Lock for each key currently being fetched.
        # This is the core of the cache stampede protection mechanism.
        self._locks: Dict[str, asyncio.Lock] = {}
        # The _locks_lock protects the _locks dictionary itself from concurrent modification.
        self._locks_lock = asyncio.Lock()

    async def startup(self):
        """
        Initializes connections for all stateful memory layers.
        This method is called once during the application's startup lifecycle.
        """
        await self.l1.connect()
        # L2/L3 clients are initialized in their constructors, but any async
        # connection logic would go here.
        logging.info("MemoryManager started up and all memory layers initialized.")

    async def shutdown(self):
        """
        Gracefully closes all stateful connections.
        This method is called once during the application's shutdown lifecycle.
        """
        await self.l1.close()
        logging.info("MemoryManager shut down successfully.")

    def _generate_cache_key(self, prefix: str, identifier: str, version: Optional[str] = None) -> str:
        """
        Creates a consistent, hashed key for caching to avoid issues with key length or special characters.
        Args:
            prefix: A category for the key (e.g., "file", "ast").
            identifier: The main identifier (e.g., file path).
            version: An optional version tag (e.g., commit hash).
        Returns:
            A SHA256 hashed key prefixed for namespacing.
        """
        key_string = f"{prefix}:{identifier}:{version or 'latest'}"
        return f"cache:{hashlib.sha256(key_string.encode()).hexdigest()}"

    async def get_file_content(self, file_path: str, commit_hash: Optional[str] = None) -> str:
        """
        Retrieves file content by its path, implementing a full L0->L1->L3 fallback
        with cache stampede protection and automatic cache back-filling.

        Args:
            file_path: The path to the file within the Git repository.
            commit_hash: The specific commit hash to retrieve. If None, uses the latest commit.

        Returns:
            The content of the file as a string.

        Raises:
            NotFoundError: If the file cannot be found in any memory layer.
            MemoryLayerError: If a critical layer (L3) fails unexpectedly.
        """
        cache_key = self._generate_cache_key("file", file_path, commit_hash)

        # --- L0 Check (Fastest Path) ---
        cached_value = self.l0.get(cache_key)
        if cached_value is not None:
            logging.debug(f"L0 cache HIT for key: {cache_key}")
            return cached_value

        # --- L1 Check ---
        try:
            cached_value = await self.l1.get(cache_key)
            if cached_value is not None:
                logging.debug(f"L1 cache HIT for key: {cache_key}")
                self.l0.set(cache_key, cached_value)  # Back-fill L0
                return cached_value
        except Exception as e:
            logging.warning(f"L1 Redis GET failed for key '{cache_key}': {e}. Proceeding to L3.")

        # --- Cache Stampede Protection ---
        # Acquire a lock specific to this key. If another request is already fetching
        # this key, we will wait here until it's done.
        async with self._locks_lock:
            lock = self._locks.setdefault(cache_key, asyncio.Lock())

        async with lock:
            # --- Double-Check Locking Pattern ---
            # Re-check L0/L1 now that we have the lock. The coroutine that acquired the
            # lock before us might have already populated the cache.
            cached_value = self.l0.get(cache_key)
            if cached_value is not None:
                logging.debug(f"L0 cache HIT (post-lock) for key: {cache_key}")
                return cached_value
            try:
                cached_value = await self.l1.get(cache_key)
                if cached_value is not None:
                    logging.debug(f"L1 cache HIT (post-lock) for key: {cache_key}")
                    self.l0.set(cache_key, cached_value)
                    return cached_value
            except Exception as e:
                 logging.warning(f"L1 Redis GET (post-lock) failed for key '{cache_key}': {e}.")

            # --- L3 Fallback Logic (Definitive Cache Miss) ---
            logging.info(f"Cache miss for key '{cache_key}'. Fetching from L3 (Git).")

            final_commit_hash = commit_hash or self.l3.get_latest_commit()
            value = self.l3.get_file_at_commit(file_path, final_commit_hash)

            if value is not None:
                logging.info(f"Found key '{file_path}' in L3. Back-filling L1 and L0 caches.")
                # Asynchronously back-fill the caches for future requests
                try:
                    await self.l1.set(cache_key, value)
                    self.l0.set(cache_key, value)
                except Exception as e:
                    logging.warning(f"Failed to back-fill cache for key '{cache_key}': {e}")

            # --- Cleanup and Return ---
            # Clean up the lock for this key once we're done to prevent memory leaks.
            async with self._locks_lock:
                self._locks.pop(cache_key, None)

            if value is None:
                raise NotFoundError(f"File '{file_path}' not found at commit '{final_commit_hash}'.")

            return value

    async def semantic_search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Performs a semantic search using the L2 ChromaDB layer."""
        logging.info(f"Performing semantic search in L2 (Chroma) for query: '{query[:50]}...'")
        try:
            return self.l2c.query(query, n_results)
        except Exception as e:
            # Wrap the original exception for better debugging
            raise MemoryLayerError("L2-Chroma", f"Semantic search failed: {e}")

    async def persist_node(self, class_name: str, data: Dict[str, Any]) -> str:
        """Persists a new data object (node) to the L2 Weaviate layer."""
        logging.info(f"Persisting node to L2 (Weaviate) in class '{class_name}'.")
        try:
            uuid = self.l2w.add_node(class_name, data)
            logging.info(f"Successfully persisted object to L2 with UUID: {uuid}")
            return uuid
        except Exception as e:
            raise MemoryLayerError("L2-Weaviate", f"Persistence failed: {e}")

    async def set_cache_item(self, key: str, value: Any, expire_seconds: int = 3600):
        """
        Explicitly sets a value in the cache layers (L0, L1), useful for storing
        computed results from AI analysis.

        Args:
            key: The unique key for the item.
            value: The value to store (should be JSON-serializable if complex).
            expire_seconds: The time-to-live for the item in the L1 cache.
        """
        logging.info(f"Setting cache for key '{key}' with TTL {expire_seconds}s.")
        self.l0.set(key, value)
        try:
            # In a real system, complex objects should be serialized to JSON strings
            value_to_store = json.dumps(value) if isinstance(value, (dict, list)) else value
            await self.l1.set(key, value_to_store, expire=expire_seconds)
        except Exception as e:
            logging.warning(f"L1 Redis SET failed for key '{key}': {e}.")

    async def ingest_document(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Indexes a document into the semantic vector store."""
        logging.info(f"Ingesting document '{doc_id}' into L2-Chroma")
        try:
            self.l2c.add_document(doc_id, content, metadata)
        except Exception as e:
            raise MemoryLayerError("L2-Chroma", f"Ingestion failed: {e}")

    async def rag_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Perform a simple RAG query using stored documents."""
        logging.info(f"Running RAG query for: '{query}'")
        search = await self.semantic_search(query, top_k)
        context = [doc for docs in search["documents"] for doc in docs]
        # Placeholder answer generation
        answer = context[0] if context else ""
        return {"answer": answer, "context": context}
