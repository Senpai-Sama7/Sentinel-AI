import requests

BASE_URL = "http://localhost:8000"
JWT = "<your_token_here>"

def ingest_file(filepath):
    with open(filepath, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/api/v1/memory/ingest",
            headers={"Authorization": f"Bearer {JWT}"},
            files={"file": f}
        )
    print(resp.status_code, resp.json())

def semantic_search(query, top_k=3):
    resp = requests.post(
        f"{BASE_URL}/api/v1/memory/search",
        headers={
            "Authorization": f"Bearer {JWT}",
            "Content-Type": "application/json"
        },
        json={"query": query, "top_k": top_k}
    )
    print(resp.status_code, resp.json())

def rag_query(query, stream=False):
    resp = requests.post(
        f"{BASE_URL}/api/v1/memory/query",
        headers={
            "Authorization": f"Bearer {JWT}",
            "Content-Type": "application/json"
        },
        json={"query": query, "stream": stream}
    )
    print(resp.status_code, resp.json())

if __name__ == "__main__":
    ingest_file("docs/spec.pdf")
    semantic_search("reset password")
    rag_query("Explain auth flow", stream=True)