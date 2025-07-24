# Architecture Diagram

```mermaid
flowchart TD
    subgraph Client
        user(User)
    end
    subgraph API[FastAPI Service]
        A[Ingest Endpoint]
        B[Search Endpoint]
        C[Query Endpoint]
    end
    subgraph L0[In-Process Cache]
    end
    subgraph L1[Redis Cache]
    end
    subgraph L2[ChromaDB]
    end
    subgraph L3[Git Repo]
    end
    subgraph LLM[External LLM]
    end

    user -->|HTTP| API
    API --> L0
    API --> L1
    API --> L2
    API --> L3
    API --> LLM
