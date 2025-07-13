--- MERMAID DIAGRAM ---

graph TD
    subgraph User/Client
        A[External Client]
    end

    subgraph "Sentinel AI Memory Service (FastAPI on K8s/Docker)"
        B[API Layer: api/routes.py]
        C[Core Logic: core/manager.py]
        D[L0: In-Process Cache]
        E[Parallel Executor]
    end

    subgraph "L1: Distributed Cache"
        F[Redis Server]
    end

    subgraph "L2: Working & Semantic Memory"
        G[Weaviate Server (Graph/Vector)]
        H[ChromaDB (Vector Store for RAG)]
    end

    subgraph "L3: Source of Truth"
        I[Git Repository (File System)]
    end

    %% Request Flow
    A -- HTTPS Request --> B

    %% Internal Logic Flow
    B -- Calls --> C

    %% Memory Hierarchy Access
    C -- 1. Check --> D
    D -- 2. Cache Miss --> C
    C -- 3. Check --> F
    F -- 4. Cache Miss --> C
    C -- 5. Fallback Read --> I
    I -- 6. Data Found --> C
    C -- 7. Back-fill --> F
    C -- 8. Back-fill --> D
    C -- 9. Return Value --> B
    B -- HTTPS Response --> A

    %% Other Interactions
    C -- Semantic Search --> H
    C -- Persist Data --> G
    C -- Offload CPU/IO Task --> E

    %% Styling
    style A fill:#cde4ff,stroke:#6a8ebf,stroke-width:2px
    style B fill:#d5f5e3,stroke:#58d68d,stroke-width:2px
    style C fill:#fff3cd,stroke:#f1c40f,stroke-width:2px
    style F fill:#f5b7b1,stroke:#e74c3c,stroke-width:2px
    style G fill:#d2b4de,stroke:#8e44ad,stroke-width:2px
    style H fill:#d2b4de,stroke:#8e44ad,stroke-width:2px
    style I fill:#aed6f1,stroke:#3498db,stroke-width:2px
