from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
import uuid
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

# ==========================================================
# main.py (4-я версия)
# Все методы CRUD + CORS
# Есть инициализация списка тремя тестовыми задачами
# ==========================================================

app = FastAPI()

# Добавить CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # разрешить все источники (для разработки)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# Модели данных (Pydantic) - Data Models
# ==========================================================

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_completed: bool = False


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        # Для совместимости с Pydantic V2: позволяет автоматически
        # преобразовывать объекты из ORM (например, SQLAlchemy) в Pydantic-модели
        from_attributes = True


# ==========================================================
# Имитация Базы Данных (In-Memory Database)
# ==========================================================
# Список для хранения задач в оперативной памяти сервера
tasks_db: List[Task] = []


# Инициализация тестовыми данными для проверки работоспособности API
def init_db():
    if not tasks_db:
        now = datetime.now()
        tasks_db.extend([
            Task(id=str(uuid.uuid4()), title="Изучить основы FastAPI",
                 description="Прочитать документацию по маршрутизации и валидации", is_completed=True, created_at=now,
                 updated_at=now),
            Task(id=str(uuid.uuid4()), title="Создать CRUD API",
                 description="Разработать эндпоинты для создания, чтения, обновления и удаления задач",
                 is_completed=False, created_at=now, updated_at=now),
            Task(id=str(uuid.uuid4()), title="Подключить фронтенд",
                 description="Развернуть простое SPA-приложение и протестировать CORS", is_completed=False,
                 created_at=now, updated_at=now),
        ])


init_db()


# ==========================================================
# Эндпоинты API (CRUD методы)
# ==========================================================

# 1. READ ALL — Получение списка всех задач
@app.get("/tasks", response_model=List[Task], status_code=status.HTTP_200_OK)
async def get_tasks():
    """
    Возвращает список всех существующих задач.
    Если задач в базе нет, вернет пустой список [].
    """
    return tasks_db


# 2. READ ONE — Получение конкретной задачи по её ID
@app.get("/tasks/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
async def get_task(task_id: str):
    """
    Ищет задачу в базе по её уникальному идентификатору (UUID).
    Если задача не найдена, генерирует ошибку 404 Not Found.
    """
    for task in tasks_db:
        if task.id == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Задача с id {task_id} не найдена"
    )


# 3. CREATE — Создание новой задачи
@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate):
    """
    Принимает JSON с полями из TaskCreate (валидирует их),
    автоматически генерирует системные поля (id, created_at, updated_at)
    и сохраняет задачу в импровизированную БД.
    """
    now = datetime.now()
    new_task = Task(
        id=str(uuid.uuid4()),  # Генерация случайного уникального ID
        title=task_data.title,
        description=task_data.description,
        is_completed=task_data.is_completed,
        created_at=now,
        updated_at=now
    )
    tasks_db.append(new_task)
    return new_task


# 4. UPDATE — Полное обновление существующей задачи (PUT)
@app.put("/tasks/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
async def update_task(task_id: str, updated_data: TaskCreate):
    """
    Находит задачу по id и полностью перезаписывает её поля переданными данными.
    Поле updated_at автоматически обновляется на текущее время.
    """
    for index, task in enumerate(tasks_db):
        if task.id == task_id:
            # Создаем новый объект Task на основе старого, обновляя изменяемые поля
            new_task = Task(
                id=task.id,
                title=updated_data.title,
                description=updated_data.description,
                is_completed=updated_data.is_completed,
                created_at=task.created_at,  # Дата создания остается прежней
                updated_at=datetime.now()  # Фиксируем время изменения
            )
            tasks_db[index] = new_task
            return new_task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Задача с id {task_id} не найдена для обновления"
    )


# 5. DELETE — Удаление задачи
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    """
    Удаляет задачу из базы по её id.
    В случае успеха возвращает статус 204 No Content (без тела ответа).
    """
    for index, task in enumerate(tasks_db):
        if task.id == task_id:
            tasks_db.pop(index)
            return  # Статус 204 автоматически не ожидает возврата тела данных

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Задача с id {task_id} не найдена для удаления"
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


def get_task_or_404(task_id: str) -> int:
    """Ищет задачу по id и возвращает её индекс в списке.
    Если не найдена — бросает ошибку 404."""
    for index, task in enumerate(tasks_db):
        if task.id == task_id:
            return index
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Задача с id {task_id} не найдена"
    )


# Исправленный эндпоинт удаления с правильными отступами
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    """
    Удаляет задачу из базы по её id с предварительной проверкой.
    """
    # Получаем индекс задачи в списке через вспомогательную функцию
    task_index = get_task_or_404(task_id)

    # Удаляем элемент по его числовому индексу
    del tasks_db[task_index]

    # Для статуса 204 No Content возвращать явный None или return не требуется,
    # Добавьте этот эндпоинт в файл main.py
    @app.get("/health")
    async def health_check():
        """
        Эндпоинт для проверки работоспособности приложения.
        """
        return {"status": "healthy"}

    # FastAPI сам сформирует пустой ответ. Но пустой return написать можно.
    return


