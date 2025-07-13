# orchestrator/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Service Addresses
GO_PROXY_GRPC_ADDR: str = os.getenv("GO_PROXY_GRPC_ADDR", "localhost:50052")

# AI Configuration
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY is not set. LLM features will fail.")

# Memory Configuration
CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "/app/chroma_data")

# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()