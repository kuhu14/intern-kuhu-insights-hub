def assert_error(response, status_code: int, code: str) -> None:
    """Check a response uses the common error shape."""
    assert response.status_code == status_code
    body = response.json()
    assert set(body) == {"error"}
    assert body["error"]["code"] == code
    assert isinstance(body["error"]["message"], str)
    assert body["error"]["message"]
