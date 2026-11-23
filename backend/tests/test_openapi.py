import json

from app.main import app
from scripts.export_openapi import OUTPUT_PATH


def test_committed_openapi_is_up_to_date():
    committed = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    hint = "docs/openapi.json is out of date - run: python -m scripts.export_openapi"
    assert committed == app.openapi(), hint
