import os
import argparse
import logging
from core.l2_weaviate import L2Weaviate
from core.ingestion_service import ingest_file

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main(repo_path: str) -> None:
    if not os.path.isdir(repo_path):
        logger.error(f"Provided path is not a directory: {repo_path}")
        return

    logger.info(f"Starting ingestion for repository: {repo_path}")
    try:
        weaviate_manager = L2Weaviate(os.environ.get("WEAVIATE_URL", "http://localhost:8080"))
    except Exception as e:
        logger.error(f"Failed to initialize WeaviateManager: {e}. Aborting.")
        return

    file_count = 0
    for root, _, files in os.walk(repo_path):
        if '.git' in root:
            continue
        for fname in files:
            file_path = os.path.join(root, fname)
            ingest_file(file_path, weaviate_manager)
            file_count += 1

    logger.info(f"Repository ingestion process complete. Scanned {file_count} files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest a Git repository and other documents into Sentinel-AI."
    )
    parser.add_argument("repo_path", type=str, help="The local path to the repository or directory of documents.")
    args = parser.parse_args()
    main(args.repo_path)
