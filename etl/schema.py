from pydantic import BaseModel, Field
from typing import Dict, Any

class ContentBlock(BaseModel):
    id: str = Field(...)
    source_id: str = Field(...)
    type: str = Field(...)
    text: str = Field(...)
    order: int = Field(...)
    metadata: Dict[str, Any] = Field(default_factory=dict)

