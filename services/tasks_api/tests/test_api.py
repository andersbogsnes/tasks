import pytest
from fastapi import status
from fastapi.testclient import TestClient

from tasks_api import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)

def test_healthcheck(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "OK"}
