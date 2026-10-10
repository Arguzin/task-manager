from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    """Проверяем, что health-check отвечает 200 и возвращает ожидаемый статус."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
