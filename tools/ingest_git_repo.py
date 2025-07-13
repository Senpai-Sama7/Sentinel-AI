import os
import sys
import logging
from git import Repo, GitCommandError
import weaviate

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.config import GIT_REPO_PATH, WEAVIATE_URL

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ingest_repository():
    if not os.path.isdir(GIT_REPO_PATH):
        logging.error(f"Git repository path not found: '{GIT_REPO_PATH}'")
        return

    try:
        repo = Repo(GIT_REPO_PATH)
        client = weaviate.Client(WEAVIATE_URL)
    except Exception as e:
        logging.error(f"Initialization failed: {e}")
        return

    commit = repo.head.commit
    commit_hash = commit.hexsha
    logging.info(f"Starting ingestion for repository at HEAD commit: {commit_hash}")

    client.batch.configure(batch_size=100, dynamic=True)

    with client.batch as batch:
        for blob in commit.tree.traverse():
            if blob.type == 'blob':
                file_path = blob.path
                try:
                    content = blob.data_stream.read().decode(errors='replace')
                    properties = {
                        "key": file_path,
                        "value": content,
                        "layer": "L3-Git",
                        "commit_hash": commit_hash,
                        "timestamp": commit.committed_datetime.isoformat(),
                    }
                    batch.add_data_object(properties, "MemoryNode")
                    logging.info(f"Queued for ingestion: {file_path}")
                except Exception as e:
                    logging.error(f"Failed to process or queue file '{file_path}': {e}")
    
    logging.info("Finished queuing all files. Ingestion is now running in the background.")

if __name__ == "__main__":
    ingest_repository()
