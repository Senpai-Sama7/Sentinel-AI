# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-07-15
### Added
- Initial production-ready semantic-memory micro-service.
- Multi-format ingestion pipeline (PDF, DOCX, Markdown, images, code).
- Vector embeddings & indexing with Chroma.
- FastAPI RAG endpoints (`/ingest`, `/search`, `/query`).
- JWT-based authentication & RBAC.
- Multi-tier caching (LRU, Redis, vector store).
- GitHub Actions CI (lint, test, build, Trivy scan).
- Helm chart & Docker Compose setup.
- 100% pytest coverage; integration, load, chaos tests.
- Prometheus metrics & OpenTelemetry traces.
- Documentation: architecture, schema, runbooks.

## [1.0.0] - 2025-07-24
- Initial release notes...
