import os
import sys
import importlib.util
from pathlib import Path
import yaml
import json

REQUIRED_DIRS = [
    "api", "core", "etl", "ai", "tests", "docs", ".github", "helm"
]
REQUIRED_ENDPOINTS = [
    "/api/v1/memory/ingest", "/api/v1/memory/search", "/api/v1/memory/query", "/api/v1/memory/file/{id}", "/health", "/metrics", "/docs", "/redoc"
]
REQUIRED_ENV_VARS = [
    "JWT_SECRET", "OPENAI_API_KEY", "REDIS_URL", "CHROMA_HOST", "CHROMA_PORT", "APP_CORS_ORIGINS", "LOG_LEVEL", "CACHE_TTL", "INGEST_BATCH_SIZE"
]

failures = []

# Check directories
for d in REQUIRED_DIRS:
    if not Path(d).exists():
        failures.append(f"Missing required directory: {d}")

# Check env vars in .env.example
with open(".env.example") as f:
    env_lines = [l.split("=")[0].strip() for l in f if l.strip() and not l.startswith("#")]
for var in REQUIRED_ENV_VARS:
    if var not in env_lines:
        failures.append(f"Missing env var in .env.example: {var}")

# Check endpoints in OpenAPI schema
try:
    import requests
    resp = requests.get("http://localhost:8000/openapi.json")
    if resp.status_code == 200:
        openapi = resp.json()
        paths = set(openapi["paths"].keys())
        for ep in REQUIRED_ENDPOINTS:
            if not any(ep.split("{")[0] in p for p in paths):
                failures.append(f"Missing endpoint in OpenAPI: {ep}")
    else:
        failures.append("Could not fetch OpenAPI schema from running API.")
except Exception as e:
    failures.append(f"Error checking OpenAPI schema: {e}")

# Check ContentBlock schema
try:
    from etl.schema import ContentBlock
    block = ContentBlock.model_json_schema()
    required_keys = {"id", "source_id", "type", "text", "order", "metadata"}
    if not required_keys.issubset(block["properties"].keys()):
        failures.append("ContentBlock schema missing required keys.")
except Exception as e:
    failures.append(f"Error checking ContentBlock schema: {e}")

if failures:
    print("\n\nSpec-check failed:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
else:
    print("Spec-check passed. All requirements are met.")