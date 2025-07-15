# API Schema (Generated)

```
# SetMemoryRequest
```
{
  "title": "SetMemoryRequest",
  "type": "object",
  "properties": {
    "key": {"title": "Key", "type": "string", "description": "The unique key for the memory item. For files, this should be the file path.", "example": "src/utils/helpers.py"},
    "value": {"title": "Value"},
    "persist_to_l2": {"title": "Persist To L2", "default": false, "type": "boolean", "description": "If true, the item will be persisted to the L2 Weaviate layer for long-term storage."}
  },
  "required": ["key", "value"]
}

```
# SemanticSearchRequest
```
{
  "title": "SemanticSearchRequest",
  "type": "object",
  "properties": {
    "query": {"title": "Query", "type": "string", "description": "The natural language query for semantic search against the L2 ChromaDB layer.", "example": "What is the purpose of the MemoryManager?"},
    "top_k": {"title": "Top K", "default": 5, "type": "integer", "minimum": 1, "maximum": 50, "description": "The number of top results to return."}
  },
  "required": ["query"]
}

```
# SetMemoryResponse
```
{
  "title": "SetMemoryResponse",
  "type": "object",
  "properties": {
    "key": {"title": "Key", "type": "string"},
    "status": {"title": "Status", "type": "string"},
    "message": {"title": "Message", "type": "string"}
  },
  "required": ["key", "status", "message"]
}

```
# SemanticSearchResponse
```
{
  "title": "SemanticSearchResponse",
  "type": "object",
  "properties": {
    "ids": {"title": "Ids", "type": "array", "items": {"type": "array", "items": {"type": "string"}}},
    "documents": {"title": "Documents", "type": "array", "items": {"type": "array", "items": {"type": "string"}}},
    "metadatas": {"title": "Metadatas", "type": "array", "items": {"type": "array", "items": {"type": "object", "additionalProperties": {}}}},
    "distances": {"title": "Distances", "type": "array", "items": {"type": "array", "items": {"type": "number"}}}
  },
  "required": ["ids", "documents", "metadatas", "distances"]
}

```
# ErrorResponse
```
{
  "title": "ErrorResponse",
  "type": "object",
  "properties": {
    "message": {"title": "Message", "type": "string"}
  },
  "required": ["message"]
}
