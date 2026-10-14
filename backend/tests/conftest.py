from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(scope="session")
def fixtures_dir():
    return FIXTURES


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """FastAPI test client whose uploads go to a temp directory."""
    from fastapi.testclient import TestClient
    from app.routers import resumes
    from app.main import app

    monkeypatch.setattr(resumes, "UPLOAD_DIR", tmp_path)
    return TestClient(app)
