# API Schema

## SetMemoryRequest

```json
{
  "description": "Defines the request body for setting or updating a memory item.",
  "properties": {
    "key": {
      "description": "The unique key for the memory item. For files, this should be the file path.",
      "example": "src/utils/helpers.py",
      "title": "Key",
      "type": "string"
    },
    "value": {
      "description": "The value to store. Can be any JSON-serializable type.",
      "title": "Value"
    },
    "persist_to_l2": {
      "default": false,
      "description": "If true, the item will be persisted to the L2 Weaviate layer for long-term storage.",
      "title": "Persist To L2",
      "type": "boolean"
    }
  },
  "required": [
    "key",
    "value"
  ],
  "title": "SetMemoryRequest",
  "type": "object"
}
```

## SemanticSearchRequest

```json
{
  "description": "Defines the request body for performing a semantic search.",
  "properties": {
    "query": {
      "description": "The natural language query for semantic search against the L2 ChromaDB layer.",
      "example": "What is the purpose of the MemoryManager?",
      "title": "Query",
      "type": "string"
    },
    "top_k": {
      "default": 5,
      "description": "The number of top results to return.",
      "exclusiveMinimum": 0,
      "maximum": 50,
      "title": "Top K",
      "type": "integer"
    }
  },
  "required": [
    "query"
  ],
  "title": "SemanticSearchRequest",
  "type": "object"
}
```
