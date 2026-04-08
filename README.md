# STO Service API

REST API для управління клієнтами та транспортними засобами СТО.

## Технології

- Python 3.12 + FastAPI
- PostgreSQL + SQLAlchemy + Alembic
- Docker + Docker Compose
- GitHub Actions CI/CD

## Запуск

```bash
docker-compose up
```

API доступне за адресою: http://localhost:8000  
Swagger документація: http://localhost:8000/docs

## Тести

```bash
pytest tests/
```
