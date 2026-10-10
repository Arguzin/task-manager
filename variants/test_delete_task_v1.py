# ==========================================================
# ВАРИАНТ 1
# В этом файле намеренно допущены ошибки.
# Задача: найти их, исправить и добиться, чтобы все тесты проходили.
# 1. Скопируйте файл в tests/ и переименуйте в test_delete_task.py
# 2. Запустите: pytest tests/ -v
# 3. Прочитайте сообщения об ошибках и исправьте код
# ==========================================================

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_delete_existing_task():
    """Успешное удаление существующей задачи."""
    response = client.post("/tasks", json={
        "title": "Временная задача",
        "description": "Будет удалена в тесте",
        "is_completed": False,
    })
    assert response.status_code == 200
    task_id = response.json()["id"]

    response = client.delete(f"/task/{task_id}")
    assert response.status_code == 204

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404


def test_delete_missing_task():
    """Попытка удалить несуществующую задачу — ожидаем 404."""
    response = client.delete("/tasks/nonexistent-id")
    assert response.status_code == 404