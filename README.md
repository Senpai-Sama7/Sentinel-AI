# Sentinel AI

[![CI](https://github.com/Senpai-sama7/Sentinel-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/Senpai-sama7/Sentinel-AI/actions/workflows/ci.yml)
[![Helm Chart](https://img.shields.io/badge/helm-chart-blue)](https://github.com/Senpai-sama7/Sentinel-AI/tree/main/helm)
[![Docker](https://img.shields.io/docker/pulls/Senpai-sama7/sentinel-memory-service)](https://hub.docker.com/r/Senpai-sama7/sentinel-memory-service)

A production-ready **semantic memory** micro-service that transforms unstructured content into actionable, AI-driven insights. Designed for high-throughput ingestion, precise semantic indexing, and Retrieval-Augmented Generation (RAG), it delivers sub-millisecond search and contextual responses.


## 🚀 Core Capabilities

- **Multi-Format Ingestion:**\
  Import PDF, DOCX, Markdown, plain text, source code, and OCR-processed images. Content is normalized into `ContentBlock` JSON models with metadata and deduplicated for efficiency.
- **Embeddings & Vector Search:**\
  Utilize Hugging Face or OpenAI embeddings and index in Chroma, Weaviate, or Milvus. Supports batch and incremental upserts with auto-sharding for scale.
- **Multi-Tier Caching:**
  - *L0 (In-Process LRU)* – Instant cache within each process.
  - *L1 (Redis)* – Distributed layer for embedding & search results.
  - *L2 (Vector Store)* – Persistent in-memory vectors.
  - *L3 (Archive)* – Raw source backups on S3 or filesystem.\
    Includes stampede protection to prevent cache storms.
- **Retrieval-Augmented Generation (RAG):**\
  Combine top-K relevant chunks with LLM prompts (OpenAI GPT-4, local Llama, others). Returns safe fallbacks when context is missing and optional streaming for chat UIs.
- **Secure FastAPI Endpoints:**
  - `POST /api/v1/memory/ingest`
  - `POST /api/v1/memory/search`
  - `POST /api/v1/memory/query`
  - `GET /api/v1/memory/file/{id}`
  - Health, metrics, and interactive docs at `/docs` and `/redoc`.
- **Authentication & RBAC:**\
  JWT with RSA/HMAC, role-based permissions (`reader`, `ingestor`, `admin`), token refresh, expiry, and audit logs.
- **Containerized & Cloud-Native:**\
  Docker Compose for local dev, Helm chart for Kubernetes. GitHub Actions drive CI/CD: Black, Ruff, mypy, pytest, codecov, Trivy, and chart linting.
- **Observability:**\
  Prometheus metrics (request rates, cache hits, RAG latency), OpenTelemetry traces (Jaeger/Tempo), and structured JSON logs (structlog) with trace IDs.
- **Quality & Resilience:**\
  100% pytest coverage, Locust load tests, chaos experiments. Self-auditing scripts ensure schema consistency and loop detection.
- **Documentation & Runbooks:**\
  C4 diagrams and Pydantic schemas, Postman collections, code snippets, and operational playbooks for incident response.
- **Graph-Based Knowledge Modeling:**\
  Weighted, directed graphs with node and edge attributes for representing assets. See [docs/knowledge_graph.md](docs/knowledge_graph.md).
- **Attack Tree Logic:**\
  Hierarchical preconditions and actions with cross-links to graph assets. See [docs/attack_tree.md](docs/attack_tree.md).
- **Reasoning Engine:**\
  Chain- and tree-of-thought parsing with branch tracking for auditability. See [docs/reasoning_engine.md](docs/reasoning_engine.md).
- **Vector Memory:**\
  Store reasoning chains and attack paths in Weaviate for later recall.
- **Rules & Reflection:**\
  Enforce hard constraints and log lessons after each run. See
  [docs/rules.md](docs/rules.md) and [docs/reflection.md](docs/reflection.md).
- **Advanced AI/ML Awareness:**\
  New modules for temporal modeling, topological analysis, multi-agent simulation,
  multi-modal fusion, and personalization. See [docs/advanced_features.md](docs/advanced_features.md).


---

## 📖 Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration](#configuration)
3. [Usage Examples](#usage-examples)
4. [Deployment](#deployment)
   - [Docker Compose](#docker-compose)
   - [Kubernetes (Helm)](#kubernetes-helm)
5. [Real Use Cases](#real-use-cases)
6. [Contributing & Governance](#contributing--governance)
7. [Changelog & Roadmap](#changelog--roadmap)
8. [License](#license)

---

## Quick Start

1. **Clone & Configure**
   ```bash
   git clone https://github.com/your-org/Sentinel-AI.git
   cd Sentinel-AI
   cp .env.example .env
   # Edit .env to set JWT_SECRET, OPENAI_API_KEY, etc.
   ```
2. **Run Locally**
   ```bash
   docker compose up --build -d
   # Visit http://localhost:8000/docs
   ```
3. **Stop & Clean**
  ```bash
  docker compose down -v
  ```

## Getting Started

1. **Install Dependencies**
   ```bash
   pip install poetry
   poetry install --with dev
   ```
2. **Run the Application**
   ```bash
   docker compose up --build -d
   ```
3. **Run the Test Suite**
   ```bash
   make test
   ```

---

## Configuration

| Env Variable        | Description                           | Default                    |
| ------------------- | ------------------------------------- | -------------------------- |
| `JWT_SECRET`        | JWT signing key                       | *REQUIRED*                 |
| `OPENAI_API_KEY`    | OpenAI embeddings & LLM API key       | *REQUIRED*                 |
| `REDIS_URL`         | Redis DSN                             | `redis://localhost:6379/0` |
| `CHROMA_HOST`       | Chroma vector DB host                 | `localhost`                |
| `CHROMA_PORT`       | Chroma vector DB port                 | `8000`                     |
| `APP_CORS_ORIGINS`  | JSON array of allowed origins         | `[]`                       |
| `LOG_LEVEL`         | Logging level (`DEBUG`, `INFO`, etc.) | `INFO`                     |
| `CACHE_TTL`         | Redis entry TTL (seconds)             | `3600`                     |
| `INGEST_BATCH_SIZE` | Docs per ingest batch                 | `8`                        |

*Extensions for Helm values are in **`helm/values.yaml`**.*

---

## Usage Examples

### Ingest a File

```bash
curl -X POST http://localhost:8000/api/v1/memory/ingest \
  -H "Authorization: Bearer $JWT" \
  -F "file=@./docs/spec.pdf"
```

**Errors**: 400 (bad file), 401 (unauthorized), 500 (server error)

### Semantic Search

```bash
curl -X POST http://localhost:8000/api/v1/memory/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT" \
  -d '{"query":"reset password","top_k":3}'
```

### RAG Query (Streaming)

```bash
curl -N -X POST http://localhost:8000/api/v1/memory/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT" \
  -d '{"query":"Explain auth flow","stream":true}'
```

### Knowledge Graph & Attack Paths

```python
from graphs.knowledge_graph import KnowledgeGraph

net = KnowledgeGraph()
net.add_asset("Server_A", os="Ubuntu", risk_score=5)
net.add_asset("DB")
net.add_connection("Server_A", "DB", type="sql", risk=8)

print(net.paths("Server_A", "DB"))
```

---

## Deployment

### Docker Compose

- Local dev and test environment.
- Services: `api`, `redis`, `chroma`.

### Kubernetes (Helm)

```bash
helm repo add semmem https://your-org.github.io/Sentinel-AI/helm
helm repo update
helm upgrade --install semmem semmem/Sentinel-AI \
  --set image.tag=$(git rev-parse --short HEAD) \
  --set env.OPENAI_API_KEY=$OPENAI
```

Customize `helm/values.yaml` for resources, ingress, and CronJobs.

---

## Real Use Cases

1. **Developer Productivity**\
   Index code repos and docs, enable semantic code search, auto-generate snippets, and summarize architecture.
2. **Enterprise Knowledge Base**\
   Ingest policies, training, and FAQs; provide employees an AI assistant; automate audit queries.
3. **Customer Support**\
   Power chatbots with manuals and KB articles, update nightly for new content, ensure role-based responses.
4. **Legal Research**\
   Semantic retrieval of case law and briefs, generate attributed summaries, find related precedents.

---

## Contributing & Governance

- **Contribute:** See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Code of Conduct:** See [CODE\_OF\_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Templates:** `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`
- **Branches:** Protected `main` & `release/*`, require 2 reviews and passing CI.

---

## Changelog & Roadmap

Review [CHANGELOG.md](CHANGELOG.md) for release history. Upcoming: multi-tenant support, hybrid keyword-vector search, enhanced streaming.

---

## Security Notice

Use this project **only** on systems you own or have explicit permission to test. Unauthorized usage is prohibited.

## License

[MIT License](LICENSE)

