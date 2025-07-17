# API Schema (Generated)

```
# SetMemoryRequest
```
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
# SemanticSearchRequest
```
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
# SetMemoryResponse
```
{
  "description": "Defines the response body after successfully setting a memory item.",
  "properties": {
    "key": {
      "title": "Key",
      "type": "string"
    },
    "status": {
      "title": "Status",
      "type": "string"
    },
    "message": {
      "title": "Message",
      "type": "string"
    }
  },
  "required": [
    "key",
    "status",
    "message"
  ],
  "title": "SetMemoryResponse",
  "type": "object"
}

```
# SemanticSearchResponse
```
{
  "description": "Defines the structured response for a semantic search query.\nMirrors the structure returned by the ChromaDB client.",
  "properties": {
    "ids": {
      "items": {
        "items": {
          "type": "string"
        },
        "type": "array"
      },
      "title": "Ids",
      "type": "array"
    },
    "documents": {
      "items": {
        "items": {
          "type": "string"
        },
        "type": "array"
      },
      "title": "Documents",
      "type": "array"
    },
    "metadatas": {
      "items": {
        "items": {
          "additionalProperties": true,
          "type": "object"
        },
        "type": "array"
      },
      "title": "Metadatas",
      "type": "array"
    },
    "distances": {
      "items": {
        "items": {
          "type": "number"
        },
        "type": "array"
      },
      "title": "Distances",
      "type": "array"
    }
  },
  "required": [
    "ids",
    "documents",
    "metadatas",
    "distances"
  ],
  "title": "SemanticSearchResponse",
  "type": "object"
}

```
# ErrorResponse
```
{
  "description": "A generic error response model for consistent error reporting.",
  "properties": {
    "message": {
      "title": "Message",
      "type": "string"
    }
  },
  "required": [
    "message"
  ],
  "title": "ErrorResponse",
  "type": "object"
}
