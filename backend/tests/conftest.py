from pathlib import Path
from contextlib import suppress

import pytest
from fastapi.testclient import TestClient

from app.main import app

DB_FILE = Path("meridian.db")


@pytest.fixture(scope="session", autouse=True)
def clean_db_once() -> None:
    if DB_FILE.exists():
        DB_FILE.unlink()
    yield
    with suppress(PermissionError):
        if DB_FILE.exists():
            DB_FILE.unlink()


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
