"""
Пустой conftest.py в корне проекта.

Его наличие заставляет pytest добавить корневую папку в sys.path,
благодаря чему тесты из tests/ могут импортировать main.py:

    from main import app
"""
