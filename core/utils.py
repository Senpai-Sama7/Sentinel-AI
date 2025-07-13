# core/utils.py
import os
import re
from pathlib import Path
from typing import Optional
import logging

def validate_file_path(file_path: str) -> str:
    """
    Validates and sanitizes file paths to prevent directory traversal attacks.

    Args:
        file_path: The file path to validate

    Returns:
        The normalized and validated file path

    Raises:
        ValueError: If the path is invalid or contains directory traversal attempts
    """
    if not file_path:
        raise ValueError("File path cannot be empty")

    # Normalize the path
    normalized = os.path.normpath(file_path)

    # Check for directory traversal attempts
    if normalized.startswith('..') or normalized.startswith('/') or '\\' in normalized:
        logging.warning(f"Potential directory traversal attempt: {file_path}")
        raise ValueError("Invalid file path: contains directory traversal or absolute path")

    # Check for suspicious patterns
    suspicious_patterns = [
        r'\.\./',  # Directory traversal
        r'\.\.\\',  # Windows directory traversal
        r'^/',      # Absolute path
        r'^[A-Z]:', # Windows drive letter
        r'\\',      # Windows backslash
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, file_path):
            logging.warning(f"Suspicious path pattern detected: {file_path}")
            raise ValueError(f"Invalid file path: contains suspicious pattern {pattern}")

    return normalized

def sanitize_cache_key(key: str) -> str:
    """
    Sanitizes cache keys to prevent injection attacks.

    Args:
        key: The cache key to sanitize

    Returns:
        The sanitized cache key
    """
    # Remove any potentially dangerous characters
    sanitized = re.sub(r'[^\w\-_.:]', '_', key)

    # Limit length to prevent DoS
    if len(sanitized) > 256:
        sanitized = sanitized[:256]

    return sanitized

def validate_commit_hash(commit_hash: str) -> str:
    """
    Validates Git commit hash format.

    Args:
        commit_hash: The commit hash to validate

    Returns:
        The validated commit hash

    Raises:
        ValueError: If the commit hash is invalid
    """
    if not commit_hash:
        raise ValueError("Commit hash cannot be empty")

    # Check if it's a valid hex string (Git commit hashes are hex)
    if not re.match(r'^[a-fA-F0-9]+$', commit_hash):
        raise ValueError("Invalid commit hash format: must be hexadecimal")

    # Check length (Git hashes are typically 40 characters, but short hashes are also valid)
    if len(commit_hash) < 7 or len(commit_hash) > 40:
        raise ValueError("Invalid commit hash length: must be between 7 and 40 characters")

    return commit_hash.lower()  # Normalize to lowercase
