from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_delete_existing_task():
    """Успешное удаление существующей задачи."""
    # 1. Создаем задачу. Исправлено: FastAPI возвращает 201 CREATED при успешном POST
    response = client.post("/tasks", json={
        "title": "Временная задача",
        "description": "Будет удалена в тесте",
        "is_completed": False,
    })
    assert response.status_code == 201  # Было: 200
    task_id = response.json()["id"]

    # 2. Удаляем задачу. Исправлено: изменен URL с "/task/..." на "/tasks/..."
    response = client.delete(f"/tasks/{task_id}")  # Было: f"/task/{task_id}"
    assert response.status_code == 204

    # 3. Проверяем, что задача больше не существует
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404


def test_delete_missing_task():
    """Попытка удалить несуществующую задачу — ожидаем 404."""
    response = client.delete("/tasks/nonexistent-id")
    assert response.status_code == 404
