# core/config.py

import os
from dotenv import load_dotenv

# load_dotenv() will search for a .env file in the project root and load its
# key-value pairs as environment variables. This is ideal for local development.
# In production (e.g., Kubernetes), these variables would be set directly in the environment.
load_dotenv()

# --- Logging Configuration ---
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

# --- L1 Cache Configuration ---
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# --- L2 Memory Configuration ---
WEAVIATE_URL: str = os.getenv("WEAVIATE_URL", "http://localhost:8080")
CHROMA_PATH: str = os.getenv("CHROMA_PATH", "./chroma_data")

# --- L3 Source of Truth Configuration ---
GIT_REPO_PATH: str = os.getenv("GIT_REPO_PATH", "./sample_repo")

# --- L0 Cache Configuration ---
L0_CACHE_SIZE: int = int(os.getenv("L0_CACHE_SIZE", "10000"))

# --- Security & API Keys ---
# It's good practice to centralize access to secrets, even if they are just
# being read from the environment.
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")