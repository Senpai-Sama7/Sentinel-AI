# orchestrator/api/models.py
from pydantic import BaseModel, Field
from typing import Optional

class AnalysisRequest(BaseModel):
    """Request model for code analysis."""
    file_path: str = Field(..., description="Path to the file to analyze")
    git_commit_hash: str = Field("latest", description="Git commit hash to analyze")
    query: str = Field(..., description="Natural language query about the code")

class AnalysisResponse(BaseModel):
    """Response model for code analysis."""
    answer: str = Field(..., description="AI-generated answer to the query")
    graph_context: str = Field(..., description="Context from AST graph analysis")
    rag_context: str = Field(..., description="Context from documentation search")
