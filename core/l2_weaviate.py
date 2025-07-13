# core/l2_weaviate.py

import weaviate
from typing import Any, Dict, Optional, List
from uuid import UUID
import logging

from .exceptions import MemoryLayerError

class L2Weaviate:
    """
    A robust, production-ready client for the L2 graph/vector memory layer,
    powered by Weaviate. This class handles storing and querying structured
    data like Abstract Syntax Trees (ASTs) and their relationships.
    """

    def __init__(self, url: str):
        """
        Initializes the Weaviate client and verifies the connection.

        Args:
            url: The URL for the Weaviate instance (e.g., "http://localhost:8080").

        Raises:
            MemoryLayerError: If the connection to Weaviate cannot be established or
                              if the server is not in a ready state.
        """
        try:
            logging.info(f"Initializing L2 Weaviate client for URL: {url}")
            # The Weaviate client manages its own connection pooling.
            self.client = weaviate.Client(url)
            if not self.client.is_ready():
                # This is a critical check for service startup.
                raise ConnectionError("Weaviate server is not ready. Please check its status.")
            logging.info("L2 Weaviate connection established and verified.")
        except Exception as e:
            raise MemoryLayerError(layer="L2-Weaviate", message=f"Failed to connect or initialize: {e}") from e

    def add_node(self, class_name: str, data: Dict[str, Any], uuid: Optional[UUID] = None) -> str:
        """
        Adds a single data object (a "node" in our graph) to Weaviate.

        Args:
            class_name: The name of the class (e.g., "MemoryNode", "ASTNode") to add the object to.
            data: A dictionary of the object's properties, matching the class schema.
            uuid: An optional pre-defined UUID for the object.

        Returns:
            The UUID of the created object as a string.

        Raises:
            MemoryLayerError: If the object creation fails.
        """
        try:
            result_uuid = self.client.data_object.create(
                data_object=data,
                class_name=class_name,
                uuid=uuid
            )
            return result_uuid
        except Exception as e:
            raise MemoryLayerError(
                layer="L2-Weaviate", 
                message=f"Failed to add node to class '{class_name}': {e}"
            ) from e

    def get_node_by_uuid(self, uuid: str, class_name: str, properties: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single node from Weaviate by its UUID.

        Args:
            uuid: The UUID of the object to retrieve.
            class_name: The class of the object.
            properties: A list of properties to return. If None, returns all properties.

        Returns:
            The object's properties as a dictionary, or None if not found.
        """
        try:
            # The `with_where` filter is the standard way to perform key-based lookups.
            result = self.client.query.get(
                class_name, 
                properties or ["*"] # Fetch all properties if none are specified
            ).with_where({
                "path": ["id"],
                "operator": "Equal",
                "valueString": uuid
            }).with_limit(1).do()
            
            nodes = result.get("data", {}).get("Get", {}).get(class_name, [])
            return nodes[0] if nodes else None
        except Exception as e:
            raise MemoryLayerError(
                layer="L2-Weaviate", 
                message=f"Failed to get node by UUID '{uuid}': {e}"
            ) from e

    def semantic_search(self, class_name: str, query: str, properties: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a semantic vector search (nearText) in Weaviate.
        This requires a vectorizer module (e.g., text2vec-openai) to be enabled on the class.

        Args:
            class_name: The class to search within.
            query: The natural language query string.
            properties: The properties to return for each result.
            limit: The maximum number of results to return.

        Returns:
            A list of result objects, each being a dictionary of properties.
        """
        try:
            near_text_filter = {"concepts": [query]}
            
            result = self.client.query.get(class_name, properties) \
                .with_near_text(near_text_filter) \
                .with_limit(limit) \
                .do()
                
            return result.get("data", {}).get("Get", {}).get(class_name, [])
        except Exception as e:
            raise MemoryLayerError(
                layer="L2-Weaviate",
                message=f"Semantic search failed for query '{query[:50]}...': {e}"
            ) from e
