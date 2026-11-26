from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_sales_service
from app.main import app
from tests.helpers import assert_error


@pytest.mark.parametrize(
    "url",
    [
        "/sales?page_size=500",
        "/sales?page_size=0",
        "/sales?page=0",
        "/sales/summary?date_from=2025-13-01",
        "/sales/summary?region=Mars",
        "/sales?channel=Online",
        "/sales/summary?group_by=weekday",
        "/sales?date_from=1764547200",
        "/sales?date_from=2025-12-31&date_to=2025-12-01",
        "/sales?is_return=maybe",
    ],
)
def test_invalid_input_returns_422_in_error_shape(client, url):
    assert_error(client.get(url), 422, "VALIDATION_ERROR")


def test_validation_message_names_the_field(client):
    response = client.get("/sales?page_size=500")
    assert response.json()["error"]["message"].startswith("page_size:")


@pytest.mark.parametrize("path", ["/sales", "/sales/summary"])
def test_unknown_sku_returns_404(client, path):
    response = client.get(path, params={"sku_code": "NOPE-1"})
    assert_error(response, 404, "SKU_NOT_FOUND")
    assert "NOPE-1" in response.json()["error"]["message"]


def test_known_sku_filter_works(client):
    body = client.get("/sales", params={"sku_code": "EM-1003"}).json()
    assert body["total"] > 0
    assert all(item["sku_code"] == "EM-1003" for item in body["items"])


def test_unknown_brand_is_empty_not_404(client):
    response = client.get("/sales", params={"brand": "NoSuchBrand"})
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_unknown_route_uses_error_shape(client):
    assert_error(client.get("/does-not-exist"), 404, "NOT_FOUND")


def test_wrong_method_uses_error_shape(client):
    assert_error(client.post("/health"), 405, "METHOD_NOT_ALLOWED")


def test_unexpected_error_hides_details():
    class BrokenService:
        def regions(self):
            raise RuntimeError("secret internal detail")

    app.dependency_overrides[get_sales_service] = BrokenService
    try:
        with TestClient(app, raise_server_exceptions=False) as broken_client:
            response = broken_client.get("/regions")
    finally:
        app.dependency_overrides.clear()

    assert_error(response, 500, "INTERNAL_ERROR")
    assert "secret" not in response.text


def test_routers_do_not_use_pandas():
    routers_dir = Path(__file__).resolve().parents[1] / "app" / "routers"
    for router_file in routers_dir.glob("*.py"):
        assert "pandas" not in router_file.read_text(), router_file.name
