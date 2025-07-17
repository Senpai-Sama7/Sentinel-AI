import json
from pathlib import Path
from api.models import (
    SetMemoryRequest,
    SemanticSearchRequest,
    SetMemoryResponse,
    SemanticSearchResponse,
    ErrorResponse,
)

models = [
    SetMemoryRequest,
    SemanticSearchRequest,
    SetMemoryResponse,
    SemanticSearchResponse,
    ErrorResponse,
]

lines = ["# API Schema (Generated)", ""]
for model in models:
    lines.append("```")
    lines.append(f"# {model.__name__}")
    lines.append("```")
    schema = model.model_json_schema()
    lines.append(json.dumps(schema, indent=2))
    lines.append("")

Path("docs/schema.md").write_text("\n".join(lines))
