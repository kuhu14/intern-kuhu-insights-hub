from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    """One client for the whole test run; `with` runs startup so the CSV loads."""
    with TestClient(app) as test_client:
        yield test_client
