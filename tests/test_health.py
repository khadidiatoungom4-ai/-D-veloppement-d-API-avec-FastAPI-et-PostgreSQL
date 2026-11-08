
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db


def test_health_ok():
    class FakeDB:
        def execute(self, query):
            return 1

    def override_get_db():
        yield FakeDB()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    finally:
        app.dependency_overrides.clear()
