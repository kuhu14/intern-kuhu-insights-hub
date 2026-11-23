"""Write the API's OpenAPI schema to docs/openapi.json.

Run from backend/:  python -m scripts.export_openapi
"""

import json
from pathlib import Path

from app.main import app

# export_openapi.py -> scripts/ -> backend/ -> repo root
OUTPUT_PATH = Path(__file__).resolve().parents[2] / "docs" / "openapi.json"


def main() -> None:
    schema = app.openapi()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",  # LF endings, matching .gitattributes
    )
    print(f"Wrote {OUTPUT_PATH} ({len(schema['paths'])} paths)")


if __name__ == "__main__":
    main()
