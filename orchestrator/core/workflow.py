# orchestrator/core/workflow.py
import logging
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from orchestrator.core.grpc_client import grpc_client
from orchestrator.models import ast_service_pb2
from orchestrator.core.rag import RAGSystem

# --- State Definition ---
class AnalysisState(TypedDict):
    query: str
    file_path: str
    git_commit_hash: str
    graph_context: str
    rag_context: str
    combined_context: str
    reasoning: str
    final_answer: str
    error: str | None

# --- Initializing Components ---
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.1)
rag_system = RAGSystem()

# --- Workflow Nodes ---
async def get_graph_context(state: AnalysisState) -> AnalysisState:
    logging.info("Workflow: Fetching graph context...")
    try:
        stub = grpc_client.get_ast_stub()
        request = ast_service_pb2.GetASTNodesRequest(
            file_path_filter=state["file_path"],
            git_commit_hash_filter=state["git_commit_hash"],
            limit=15
        )
        response = await stub.GetASTNodes(request)
        
        context_lines = [f"AST context for {state['file_path']} at commit {state['git_commit_hash'][:7]}:"]
        for node in response.ast_nodes:
            context_lines.append(f"- Node(type='{node.node_type}', name='{node.name}', snippet='{node.source_code_snippet[:50].strip()}...')")
        
        state["graph_context"] = "\n".join(context_lines)
    except Exception as e:
        logging.error(f"Error in get_graph_context: {e}")
        state["error"] = "Failed to retrieve graph context."
        state["graph_context"] = "Not available due to an error."
    return state

async def get_rag_context(state: AnalysisState) -> AnalysisState:
    logging.info("Workflow: Fetching RAG context...")
    try:
        rag_results = await rag_system.query(state["query"])
        state["rag_context"] = rag_results or "No relevant documentation found."
    except Exception as e:
        logging.error(f"Error in get_rag_context: {e}")
        state["error"] = "Failed to retrieve RAG context."
        state["rag_context"] = "Not available due to an error."
    return state

def combine_context(state: AnalysisState) -> AnalysisState:
    logging.info("Workflow: Combining contexts...")
    state["combined_context"] = (
        f"### Code Graph Context\n{state['graph_context']}\n\n"
        f"### Documentation (RAG) Context\n{state['rag_context']}"
    )
    return state

async def generate_answer(state: AnalysisState) -> AnalysisState:
    logging.info("Workflow: Generating final answer with LLM using CoT...")
    if state.get("error"):
        state["final_answer"] = f"Could not generate an answer due to a preceding error: {state['error']}"
        return state

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a senior software architect. Provide a step-by-step reasoning followed by a clear final answer.",
        ),
        (
            "human",
            "User Query: {query}\n\n--- Combined Context ---\n{context}\n\nLet's reason step by step.",
        ),
    ])
    chain = prompt | llm
    response = await chain.ainvoke({"query": state["query"], "context": state["combined_context"]})
    state["reasoning"] = response.content
    state["final_answer"] = response.content
    return state

# --- Graph Assembly ---
def create_analysis_graph() -> StateGraph:
    workflow = StateGraph(AnalysisState)
    workflow.add_node("get_graph_context", get_graph_context)
    workflow.add_node("get_rag_context", get_rag_context)
    workflow.add_node("combine_context", combine_context)
    workflow.add_node("generate_answer", generate_answer)

    # Run graph and RAG retrieval in parallel
    workflow.set_entry_point(["get_graph_context", "get_rag_context"])
    
    # After both parallel steps are done, move to combine_context
    workflow.add_edge(["get_graph_context", "get_rag_context"], "combine_context")
    workflow.add_edge("combine_context", "generate_answer")
    workflow.add_edge("generate_answer", END)
    
    return workflow.compile()

# Compile the graph once on startup
analysis_graph = create_analysis_graph()