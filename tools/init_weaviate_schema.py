import weaviate
import logging
import time
import sys
import os

# Add project root to path to allow imports from core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.config import WEAVIATE_URL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# The authoritative schema for our memory system
SCHEMA = {
    "classes": [
        {
            "class": "MemoryNode",
            "description": "A generic node representing a piece of memory, often from a Git repository.",
            "properties": [
                {"name": "key", "dataType": ["text"], "description": "Unique identifier, e.g., file path."},
                {"name": "value", "dataType": ["text"], "description": "The content of the memory node."},
                {"name": "layer", "dataType": ["string"], "description": "The memory layer of origin (e.g., 'L3-Git')."},
                {"name": "commit_hash", "dataType": ["string"], "description": "The Git commit hash for versioning."},
                {"name": "timestamp", "dataType": ["date"], "description": "Timestamp of the commit or creation."},
            ],
            "vectorizer": "none"
        },
        {
            "class": "Documentation",
            "description": "Represents a piece of documentation for semantic search (RAG).",
            "properties": [
                {"name": "content", "dataType": ["text"]},
                {"name": "source", "dataType": ["string"]},
            ],
        }
    ]
}

def main():
    max_retries = 5
    retry_delay = 10
    for attempt in range(max_retries):
        try:
            client = weaviate.Client(WEAVIATE_URL)
            if client.is_ready():
                logging.info("Successfully connected to Weaviate.")
                existing_schema = client.schema.get()
                existing_classes = {cls['class'] for cls in existing_schema.get('classes', [])}
                for class_def in SCHEMA["classes"]:
                    if class_def["class"] not in existing_classes:
                        logging.info(f"Creating class: {class_def['class']}")
                        client.schema.create_class(class_def)
                    else:
                        logging.info(f"Class already exists: {class_def['class']}")
                return
        except Exception as e:
            logging.warning(f"Could not connect to Weaviate on attempt {attempt + 1}/{max_retries}: {e}")
        if attempt < max_retries - 1:
            logging.info(f"Waiting {retry_day} seconds before next attempt...")
            time.sleep(retry_delay)
    logging.critical("Failed to initialize Weaviate schema after multiple retries.")
    sys.exit(1)

if __name__ == "__main__":
    main()
