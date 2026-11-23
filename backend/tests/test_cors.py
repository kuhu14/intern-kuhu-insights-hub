ALLOWED = "http://localhost:3000"
ALLOW_ORIGIN = "access-control-allow-origin"


def test_cors_allows_local_frontend(client):
    response = client.get("/health", headers={"Origin": ALLOWED})
    assert response.headers[ALLOW_ORIGIN] == ALLOWED


def test_cors_ignores_other_origins(client):
    for origin in [
        "http://evil.example.com",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]:
        response = client.get("/health", headers={"Origin": origin})
        assert ALLOW_ORIGIN not in response.headers, origin


def test_cors_preflight_allowed_origin(client):
    response = client.options(
        "/sales",
        headers={"Origin": ALLOWED, "Access-Control-Request-Method": "GET"},
    )
    assert response.status_code == 200
    assert response.headers[ALLOW_ORIGIN] == ALLOWED


def test_cors_preflight_rejects_other_origin(client):
    response = client.options(
        "/sales",
        headers={
            "Origin": "http://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 400
    assert ALLOW_ORIGIN not in response.headers
