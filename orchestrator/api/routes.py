# orchestrator/api/routes.py
from fastapi import APIRouter, HTTPException, status
import logging

from orchestrator.core.workflow import analysis_graph
from orchestrator.api.models import AnalysisRequest, AnalysisResponse

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_code(request: AnalysisRequest):
    """Triggers the full code analysis workflow."""
    logging.info(f"Received analysis request for file: {request.file_path}")
    initial_state = {
        "file_path": request.file_path,
        "git_commit_hash": request.git_commit_hash,
        "query": request.query,
    }
    
    try:
        final_state = await analysis_graph.ainvoke(initial_state)
        if final_state.get("error"):
            # The error was handled gracefully within the workflow, but we should report it.
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=final_state["error"])
        
        return AnalysisResponse(
            answer=final_state.get("final_answer", "No answer generated."),
            graph_context=final_state.get("graph_context", ""),
            rag_context=final_state.get("rag_context", "")
        )
    except Exception as e:
        logging.error(f"Critical workflow error: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))