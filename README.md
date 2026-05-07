# Контрольная работа 4

## Запуск
pip install -r requirements.txt
alembic upgrade head
uvicorn app:app --reload

## Миграции
alembic revision --autogenerate -m "message"
alembic upgrade head

## Тестирование
pytest tests/ -v

## Сценарии
POST /users - создание пользователя
GET /users/{id} - получение
DELETE /users/{id} - удаление
POST /products - создание товара
GET /products/{id} - получение товара
