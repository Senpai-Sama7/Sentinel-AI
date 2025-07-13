      
# Sentinel AI Memory Service

A production-grade, high-performance, multi-layered memory system for AI and code analysis agents. Built for enterprise scale, parallelism, and resilience.

## Core Architecture

This service implements a sophisticated multi-layered memory hierarchy to provide optimal performance for diverse data access patterns:

-   **L0 (Hot Cache):** A thread-safe, in-process LRU cache for single-process, sub-millisecond latency.
-   **L1 (Warm Cache):** A distributed Redis cache for shared, low-latency access across all service replicas.
-   **L2 (Working Memory):**
    -   **Weaviate:** A graph/vector database for storing and querying structured data like Abstract Syntax Trees (ASTs).
    -   **ChromaDB:** A vector store for semantic search over unstructured data (documentation, etc.) to power Retrieval-Augmented Generation (RAG).
-   **L3 (Persistent Truth):** A Git repository, acting as the version-controlled, authoritative source for all code.

## Advanced Features

-   **Full Cache Fallback:** Requests automatically cascade from L0 down to L3, ensuring data is found wherever it exists.
-   **Cache Back-filling:** Data retrieved from slower layers (L2/L3) is automatically written back to faster layers (L1/L0) to accelerate future access.
-   **Cache Stampede Protection:** A per-key `asyncio.Lock` mechanism prevents the "thundering herd" problem, where multiple concurrent requests for a missing key would otherwise overwhelm backend systems.
-   **Resilient & Asynchronous:** Built entirely on `asyncio` for high throughput. Failures in one memory layer (e.g., Redis outage) are gracefully handled, allowing the system to continue operating with data from other layers.
-   **Structured Logging:** All logs are emitted as JSON for easy parsing, filtering, and analysis in production monitoring systems (like ELK Stack or Datadog).
-   **Dependency Injection:** Utilizes FastAPI's dependency system for robust lifecycle management and enhanced testability.

## Project Structure

    

/sentinel_memory_service/
├── api/ # FastAPI routers, models, and dependencies
├── core/ # Core business logic, memory layers, and configuration
├── tests/ # Unit and integration tests
├── tools/ # Standalone scripts for DB setup and data ingestion
├── .env # Local environment configuration
├── main.py # Application entry point
├── pyproject.toml # Dependency management with Poetry
└── README.md # This file
Generated code

      
## Local Development Setup

### 1. Prerequisites
-   Python 3.11+
-   Docker and Docker Compose
-   Poetry (for Python dependency management)

### 2. Environment Configuration
Create a `.env` file in the project root by copying the template below. Create a sample Git repository for testing.
```bash
# Create a sample repository for L3
git init sample_repo
cd sample_repo
echo "def main():\n    print('hello world')" > main.py
git add .
git commit -m "Initial commit"
cd ..

    

# Create the .env file
cp .env.example .env 
# (Or manually create .env and fill it out)
      
# .env
LOG_LEVEL=INFO
REDIS_URL=redis://localhost:6379/0
WEAVIATE_URL=http://localhost:8080
CHROMA_PATH=./chroma_data
GIT_REPO_PATH=./sample_repo
L0_CACHE_SIZE=10000

    
3. Start Dependencies

A docker-compose.yml should be provided to run Redis and Weaviate.
Generated bash

      
docker-compose up -d

    
4. Install Python Dependencies
Generated bash

      
poetry install

    
5. Initialize Database & Ingest Data

These scripts prepare the L2 memory layer.
Generated bash

      
# 1. Create the schema in Weaviate
poetry run python -m tools.init_weaviate_schema

# 2. Ingest the sample Git repo into Weaviate
poetry run python -m tools.ingest_git_repo

    

6. Run the Service
Generated bash

      
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload



The API is now available at http://localhost:8000. Interactive documentation can be found at http://localhost:8000/docs.
Running Tests

The project uses pytest for testing. Mocks are used for external services.
Generated bash

      
poetry run pytest



To ensure code quality, run mypy for static type checking.
Generated bash

      
poetry run mypy .

    
API Endpoints

The service is versioned under /api/v1/.

    GET /api/v1/memory/file/{file_path}: Retrieves file content from the Git repository via the memory hierarchy.

    POST /api/v1/memory/search: Performs a semantic search using the L2 ChromaDB layer.

    POST /api/v1/memory/cache: Sets a value in the cache layers and optionally persists it to L2 Weaviate.

Refer to the OpenAPI documentation at /docs for detailed request/response models.
Contributing

Contributions are welcome! Please follow these steps:

    Fork the repository.

    Create a new feature branch (git checkout -b feature/amazing-feature).

    Make your changes and add tests.

    Ensure all tests and linters pass.

    Submit a pull request.

License

This project is licensed under the MIT License - see the LICENSE.md file for details.
    
