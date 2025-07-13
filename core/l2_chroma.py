# core/l2_chroma.py

import chromadb
from typing import Optional, Dict, Any, List
import logging

from .exceptions import MemoryLayerError

class L2Chroma:
    """
    A production-ready client for the L2 semantic memory layer (RAG),
    powered by ChromaDB. This class handles the storage and retrieval of
    unstructured text data (like documentation) for semantic search.
    """

    def __init__(self, path: str, collection_name: str = "project_documentation"):
        """
        Initializes the ChromaDB client with persistent storage.

        Args:
            path: The file path for ChromaDB's persistent storage directory.
            collection_name: The name of the collection to use for documents.

        Raises:
            MemoryLayerError: If the client cannot be initialized.
        """
        try:
            logging.info(f"Initializing L2 ChromaDB client with persistent path: '{path}'")
            # PersistentClient ensures data survives application restarts.
            self.client = chromadb.PersistentClient(path=path)
            
            # get_or_create_collection is an idempotent operation, making it safe
            # to run on every application startup.
            self.collection = self.client.get_or_create_collection(name=collection_name)
            logging.info(f"L2 ChromaDB connection established. Using collection: '{collection_name}'.")
        except Exception as e:
            raise MemoryLayerError(
                layer="L2-Chroma",
                message=f"Failed to initialize ChromaDB at path '{path}': {e}"
            ) from e

    def add_document(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Adds or updates a document in the ChromaDB collection. This operation is idempotent.

        Args:
            doc_id: A unique string identifier for the document.
            content: The text content of the document to be vectorized and stored.
            metadata: A dictionary of metadata (e.g., source file, URL) associated with the document.

        Raises:
            MemoryLayerError: If the document cannot be added.
        """
        try:
            # `upsert` is the preferred method for adding data as it handles both
            # new document creation and updates for existing IDs seamlessly.
            self.collection.upsert(
                ids=[doc_id],
                documents=[content],
                metadatas=[metadata or {}]
            )
            logging.debug(f"Upserted document with ID '{doc_id}' into ChromaDB.")
        except Exception as e:
            raise MemoryLayerError(
                layer="L2-Chroma",
                message=f"Failed to add document with ID '{doc_id}': {e}"
            ) from e

    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Queries the collection for documents semantically similar to the query text.

        Args:
            query_text: The natural language text to search for.
            n_results: The maximum number of results to return.

        Returns:
            A dictionary containing the query results, structured according to
            ChromaDB's API (e.g., with keys 'ids', 'documents', 'metadatas', 'distances').
            
        Raises:
            MemoryLayerError: If the query operation fails.
        """
        try:
            # The query operation automatically uses the collection's configured
            # embedding function to vectorize the query_text before searching.
            return self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
        except Exception as e:
            raise MemoryLayerError(
                layer="L2-Chroma",
                message=f"Query failed for text '{query_text[:50]}...': {e}"
            ) from e
