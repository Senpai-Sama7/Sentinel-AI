import json
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pydantic import BaseModel
from api.models import SetMemoryRequest, SemanticSearchRequest

def generate_schema():
    """Generates a markdown file with the JSON schema for the API models."""
    models = [SetMemoryRequest, SemanticSearchRequest]
    with open('docs/schema.md', 'w') as f:
        f.write("# API Schema\n\n")
        for model in models:
            f.write(f"## {model.__name__}\n\n")
            f.write("```json\n")
            f.write(json.dumps(model.model_json_schema(), indent=2))
            f.write("\n```\n\n")

if __name__ == "__main__":
    generate_schema()
