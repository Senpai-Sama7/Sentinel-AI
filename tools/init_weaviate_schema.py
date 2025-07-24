import os
import weaviate
from core.l2_weaviate import L2Weaviate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_schemas(client: weaviate.Client):
    """Creates all necessary schemas in Weaviate."""
    code_schema = {
        "class": "Code",
        "description": "A class to store code snippets and AST data",
        "vectorizer": "text2vec-openai",
        "moduleConfig": {
            "text2vec-openai": {"model": "ada", "modelVersion": "002", "type": "text"}
        },
        "properties": [
            {"name": "file_path", "dataType": ["text"], "description": "The full path to the source file."},
            {"name": "content", "dataType": ["text"], "description": "The raw code content or snippet."},
        ],
    }
    if not client.schema.exists("Code"):
        client.schema.create_class(code_schema)
        logger.info("Created 'Code' schema.")
    else:
        logger.info("'Code' schema already exists.")

    document_schema = {
        "class": "Document",
        "description": "A class to store chunks from generic documents (PDF, MD, TXT)",
        "vectorizer": "text2vec-openai",
        "moduleConfig": {
            "text2vec-openai": {"model": "ada", "modelVersion": "002", "type": "text"}
        },
        "properties": [
            {"name": "source", "dataType": ["text"], "description": "The name of the source file"},
            {"name": "content", "dataType": ["text"], "description": "The text chunk from the document"},
            {"name": "document_type", "dataType": ["text"], "description": "The file type of the document (e.g., .pdf, .md)"},
        ],
    }
    if not client.schema.exists("Document"):
        client.schema.create_class(document_schema)
        logger.info("Created 'Document' schema.")
    else:
        logger.info("'Document' schema already exists.")


def main():
    try:
        weaviate_manager = L2Weaviate(os.environ.get("WEAVIATE_URL", "http://localhost:8080"))
        client = weaviate_manager.client
        create_schemas(client)
        logger.info("Schema initialization process complete.")
    except Exception as e:
        logger.error(f"Failed to initialize Weaviate schemas: {e}")


if __name__ == "__main__":
    main()
