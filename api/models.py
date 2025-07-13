# api/models.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- Request Models ---

class SetMemoryRequest(BaseModel):
    """
    Defines the request body for setting or updating a memory item.
    """
    key: str = Field(
        ..., 
        description="The unique key for the memory item. For files, this should be the file path.",
        example="src/utils/helpers.py"
    )
    value: Any = Field(
        ..., 
        description="The value to store. Can be any JSON-serializable type."
    )
    persist_to_l2: bool = Field(
        False, 
        description="If true, the item will be persisted to the L2 Weaviate layer for long-term storage."
    )

class SemanticSearchRequest(BaseModel):
    """
    Defines the request body for performing a semantic search.
    """
    query: str = Field(
        ..., 
        description="The natural language query for semantic search against the L2 ChromaDB layer.",
        example="What is the purpose of the MemoryManager?"
    )
    top_k: int = Field(
        5, 
        gt=0, 
        le=50, 
        description="The number of top results to return."
    )

# --- Response Models ---

class SetMemoryResponse(BaseModel):
    """
    Defines the response body after successfully setting a memory item.
    """
    key: str
    status: str
    message: str

class SemanticSearchResponse(BaseModel):
    """
    Defines the structured response for a semantic search query.
    Mirrors the structure returned by the ChromaDB client.
    """
    ids: List[List[str]]
    documents: List[List[str]]
    metadatas: List[List[Dict[str, Any]]]
    distances: List[List[float]]

class ErrorResponse(BaseModel):
    """
    A generic error response model for consistent error reporting.
    """
    message: str
    
