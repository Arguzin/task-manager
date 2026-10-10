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
# Есть иициализация списка тремя тестовыми задачами
# ==========================================================

app = FastAPI()

# Добавить CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # разрешить все источники (для разработки)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Модели данных (Pydantic) - Data Models
# ==========================================================

# Базовая модель задачи — общие атрибуты, используемые
# и при создании, и при ответе, и при обновлении.
# Поля имеют валидацию: title не пустой и не длиннее 100 символов,
# description опционален и не длиннее 500.
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_completed: bool = False

# Модель для создания задачи — пока полностью повторяет TaskBase,
# но выделена отдельно, чтобы в будущем добавлять поля,
# которые нужны ТОЛЬКО при создании (например, приоритет,
# дедлайн и т.п.), не затрагивая другие модели.
# Это также делает API-документацию (Swagger) более понятной:
# для POST /tasks используется одна схема, для GET /tasks — другая.
class TaskCreate(TaskBase):
    pass

# Модель для ответа (представления) задачи — включает все поля TaskBase
# плюс системные поля, которые генерируются сервером: id, даты.
# Используется во всех эндпоинтах, возвращающих задачу (GET, POST, PUT).
class Task(TaskBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        # Для совместимости с Pydantic V2: позволяет автоматически
        # преобразовывать объекты (например, из БД) в Pydantic-модели.
        from_attributes = True


# In-memory database
tasks_db = {}
# === Инициализация тремя тестовыми задачами ===
initial_data = [
    {"title": "Изучить FastAPI", "description": "Прочитать документацию и сделать CRUD", "is_completed": False},
    {"title": "Реализовать CRUD", "description": "Написать код для каждого эндпоинта", "is_completed": False},
    {"title": "Написать тесты", "description": "Покрыть pytest все эндпоинты", "is_completed": False},
]

for data in initial_data:
    task_id = str(uuid.uuid4())
    current_time = datetime.now()
    new_task = Task(
        id=task_id,
        created_at=current_time,
        updated_at=current_time,
        **data
    )
    tasks_db[task_id] = new_task

# Helper functions
def get_task_or_404(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return tasks_db[task_id]

# Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Task Manager API", 
        "docs": "/docs",
        "tasks_endpoint": "/tasks"
    }

@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    return list(tasks_db.values())

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    task_id = str(uuid.uuid4())
    current_time = datetime.now()
    
    new_task = Task(
        id=task_id,
        created_at=current_time,
        updated_at=current_time,
         **task.model_dump()   # Pydantic V2: model_dump вместо dict
    )
    
    tasks_db[task_id] = new_task
    return new_task

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    return get_task_or_404(task_id)

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskCreate):
    task = get_task_or_404(task_id)
    
    task_data = task_update.dict()
    
    # Update task
    for key, value in task_data.items():
        setattr(task, key, value)
    
    task.updated_at = datetime.now()
    tasks_db[task_id] = task
    
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    # Добавить код метода

    return None

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
