import os
import logging
from core.l2_weaviate import L2Weaviate

logger = logging.getLogger(__name__)


def unified_search(query: str, weaviate_manager: L2Weaviate, top_k: int = 3) -> str:
    """Perform a hybrid search across Code and Document classes."""
    logger.info(f"Performing unified search for query: '{query}'")
    near_text_filter = {"concepts": [query]}
    try:
        code_results = (
            weaviate_manager.client.query.get("Code", ["file_path", "content"]).with_near_text(near_text_filter).with_limit(top_k).do()
        )
    except Exception as e:
        logger.error(f"Error querying 'Code' class in Weaviate: {e}")
        code_results = {}

    try:
        doc_results = (
            weaviate_manager.client.query.get("Document", ["source", "content"]).with_near_text(near_text_filter).with_limit(top_k).do()
        )
    except Exception as e:
        logger.error(f"Error querying 'Document' class in Weaviate: {e}")
        doc_results = {}

    context_parts = []

    code_data = code_results.get("data", {}).get("Get", {}).get("Code")
    if code_data:
        context_parts.append("--- CONTEXT FROM SOURCE CODE ---")
        for res in code_data:
            context_parts.append(f"### Source File: {res['file_path']}")
            context_parts.append("```")
            context_parts.append(res["content"])
            context_parts.append("```")
            context_parts.append("---")
        logger.info(f"Retrieved {len(code_data)} results from 'Code' class.")

    doc_data = doc_results.get("data", {}).get("Get", {}).get("Document")
    if doc_data:
        context_parts.append("\n--- CONTEXT FROM DOCUMENTS ---")
        for res in doc_data:
            context_parts.append(f"### Source Document: {res['source']}")
            context_parts.append(res["content"])
            context_parts.append("---")
        logger.info(f"Retrieved {len(doc_data)} results from 'Document' class.")

    if not context_parts:
        logger.warning("Unified search returned no results for the query.")
        return "No relevant information found in the knowledge base."

    return "\n".join(context_parts)


def generate_answer_from_query(query: str) -> str:
    """Example pipeline using the unified search."""
    try:
        weaviate_manager = L2Weaviate(os.environ.get("WEAVIATE_URL", "http://localhost:8080"))
        context = unified_search(query, weaviate_manager)
        prompt = f"""
        You are an expert AI assistant. Answer the following question based *only* on the provided context.
        If the answer is not in the context, state that you cannot answer based on the available information.

        CONTEXT:
        {context}

        QUESTION:
        {query}

        ANSWER:
        """
        logger.info("Context prepared for LLM. Returning context for inspection.")
        return prompt
    except Exception as e:
        logger.error(f"Error in RAG pipeline: {e}")
        return "An error occurred while processing your request."
