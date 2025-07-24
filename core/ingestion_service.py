import os
import logging
from typing import Set
from unstructured.partition.auto import partition
from unstructured.chunking.title import chunk_by_title

from core.l2_weaviate import L2Weaviate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CODE_EXTENSIONS: Set[str] = {".py", ".js", ".go", ".rs", ".java", ".c", ".cpp", ".h", ".ts"}
DOCUMENT_EXTENSIONS: Set[str] = {".pdf", ".md", ".txt", ".docx", ".pptx"}


def process_code_file(file_path: str, weaviate_manager: L2Weaviate) -> None:
    """Route code files to the AST parser service."""
    logger.info(f"[ROUTING: CODE] -> AST Parser for: {file_path}")
    try:
        # Placeholder for gRPC call to AST parser service
        logger.info(
            f"Placeholder: Successfully processed code file {file_path}. The real AST service would handle storage."
        )
    except Exception as e:
        logger.error(f"Failed to process code file {file_path}: {e}")


def process_document_file(file_path: str, weaviate_manager: L2Weaviate) -> None:
    """Process generic documents using unstructured."""
    logger.info(f"[ROUTING: DOCUMENT] -> Unstructured for: {file_path}")
    try:
        elements = partition(filename=file_path, strategy="auto")
        chunks = chunk_by_title(
            elements,
            max_characters=1024,
            combine_under_n_chars=512,
            new_after_n_chars=2048,
        )
        weaviate_objects = [
            {
                "source": os.path.basename(file_path),
                "content": str(chunk),
                "document_type": os.path.splitext(file_path)[1],
            }
            for chunk in chunks
        ]
        if not weaviate_objects:
            logger.warning(f"No content chunks extracted from {file_path}. Skipping storage.")
            return
        weaviate_manager.batch_import("Document", weaviate_objects)
        logger.info(
            f"Successfully processed and stored {len(weaviate_objects)} chunks from {file_path}."
        )
    except Exception as e:
        logger.error(f"Failed to process document file {file_path}: {e}")


def ingest_file(file_path: str, weaviate_manager: L2Weaviate) -> None:
    """Detect file type and route to appropriate processor."""
    if not os.path.exists(file_path):
        logger.warning(f"File not found: {file_path}. Skipping.")
        return

    _, extension = os.path.splitext(file_path)
    ext = extension.lower()
    if ext in CODE_EXTENSIONS:
        process_code_file(file_path, weaviate_manager)
    elif ext in DOCUMENT_EXTENSIONS:
        process_document_file(file_path, weaviate_manager)
    else:
        logger.warning(f"Unsupported file type: '{extension}'. Skipping {file_path}")
