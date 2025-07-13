# core/l3_git.py

import logging
from typing import Optional
from git import Repo, GitCommandError, NoSuchPathError, InvalidGitRepositoryError, BadName

from .exceptions import MemoryLayerError

class L3Git:
    """
    A robust, read-only Git-backed persistent memory layer that serves as the L3
    (Source of Truth) for all code.
    
    This class provides an interface to retrieve file contents from a specific
    version (commit hash) in a local Git repository.
    """

    def __init__(self, repo_path: str):
        """
        Initializes the Git repository object and validates the path.

        Args:
            repo_path: The local file path to the Git repository.

        Raises:
            MemoryLayerError: If the path is not a valid Git repository.
        """
        try:
            logging.info(f"Initializing L3 Git repository at path: '{repo_path}'")
            self.repo = Repo(repo_path, search_parent_directories=True)
            # A simple check to ensure it's a valid repo
            if self.repo.is_dirty(untracked_files=True):
                 logging.warning(f"L3 Git repository at '{repo_path}' has uncommitted changes or untracked files.")
            logging.info(f"L3 Git repository successfully initialized. Current HEAD: {self.repo.head.commit.hexsha[:7]}")
        except (NoSuchPathError, InvalidGitRepositoryError) as e:
            raise MemoryLayerError(
                layer="L3-Git", 
                message=f"The provided path '{repo_path}' is not a valid Git repository. Please initialize it or check the path."
            ) from e
        except Exception as e:
            raise MemoryLayerError(
                layer="L3-Git", 
                message=f"An unexpected error occurred while initializing the repository at '{repo_path}': {e}"
            ) from e

    def get_file_at_commit(self, file_path: str, commit_hash: str) -> Optional[str]:
        """
        Retrieves the contents of a file at a specific commit hash. This is the
        primary method for accessing the source of truth.

        Args:
            file_path: The relative path of the file within the repository.
            commit_hash: The full or short commit hash.

        Returns:
            The file content as a UTF-8 decoded string, or None if the file or
            commit does not exist.
        
        Raises:
            MemoryLayerError: For unexpected repository errors.
        """
        try:
            # Retrieve the commit object from the repository
            commit = self.repo.commit(commit_hash)
            
            # Traverse the commit's tree to find the file "blob"
            # The '/' operator provides an elegant way to navigate the tree.
            blob = commit.tree / file_path
            
            # Read the binary data from the blob and decode it as a string
            return blob.data_stream.read().decode('utf-8')
            
        except KeyError:
            # This specific exception is raised by GitPython if the file_path
            # does not exist in the commit's tree. We return None for "not found".
            logging.debug(f"File '{file_path}' not found in tree for commit '{commit_hash[:7]}'.")
            return None
        except BadName:
            # This exception is raised for an invalid or non-existent commit_hash.
            logging.warning(f"Invalid or non-existent commit hash provided: '{commit_hash}'.")
            return None
        except Exception as e:
            # Catch any other unexpected errors from the Git library.
            raise MemoryLayerError(
                layer="L3-Git",
                message=f"An unexpected error occurred retrieving file '{file_path}' at commit '{commit_hash}': {e}"
            ) from e

    def get_latest_commit(self) -> str:
        """
        Gets the full commit hash of the current HEAD of the repository.

        Returns:
            The 40-character hexadecimal commit hash.
            
        Raises:
            MemoryLayerError: If the HEAD cannot be resolved.
        """
        try:
            return self.repo.head.commit.hexsha
        except Exception as e:
            raise MemoryLayerError(
                layer="L3-Git",
                message=f"Could not resolve HEAD to get the latest commit hash: {e}"
            ) from e
