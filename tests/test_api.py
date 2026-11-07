import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault(
    "DATABASE_URL",
    "sqlite://",
)

from app.database import Base, get_db  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    app = create_app()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_health(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_task_crud(client: TestClient):
    created = client.post("/tasks", json={"title": "Learn GCP", "description": "VPC module"})
    assert created.status_code == 201
    task_id = created.json()["id"]

    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert any(t["id"] == task_id for t in listed.json())

    updated = client.patch(f"/tasks/{task_id}", json={"completed": True})
    assert updated.status_code == 200
    assert updated.json()["completed"] is True

    stats = client.get("/tasks/stats")
    assert stats.status_code == 200
    assert stats.json()["completed"] == 1
