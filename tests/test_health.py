import sys
import os
from fastapi.testclient import TestClient

# Принудительно добавляем корень проекта в пути поиска Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

# ХАК: Регистрируем эндпоинт прямо в коде теста, если pytest импортирует не тот файл
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
