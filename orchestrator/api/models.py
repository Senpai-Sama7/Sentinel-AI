# orchestrator/api/models.py
from pydantic import BaseModel, Field
from typing import Optional, List

class AnalysisRequest(BaseModel):
    """Request model for code analysis."""
    file_path: str = Field(..., description="Path to the file to analyze")
    git_commit_hash: str = Field("latest", description="Git commit hash to analyze")
    query: str = Field(..., description="Natural language query about the code")

class AnalysisResponse(BaseModel):
    """Response model for code analysis."""
    answer: str = Field(..., description="AI-generated answer to the query")
    reasoning: str = Field(..., description="Step-by-step reasoning leading to the answer")
    reasoning_steps: list[str] = Field(..., description="Parsed reasoning steps")
    graph_context: str = Field(..., description="Context from AST graph analysis")
    rag_context: str = Field(..., description="Context from documentation search")
