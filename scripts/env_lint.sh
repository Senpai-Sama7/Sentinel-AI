#!/usr/bin/env bash
set -e
set -a
[ -f .env ] && . .env
set +a
missing=0
for var in JWT_SECRET OPENAI_API_KEY REDIS_URL CHROMA_HOST CHROMA_PORT APP_CORS_ORIGINS LOG_LEVEL WEAVIATE_URL GIT_REPO_PATH L0_CACHE_SIZE GO_PROXY_GRPC_ADDR CHROMA_DB_PATH; do
  if [ -z "${!var}" ]; then
    echo "Missing required env var: $var" >&2
    missing=1
  fi
done
exit $missing
