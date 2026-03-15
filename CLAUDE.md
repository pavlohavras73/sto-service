# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands must be run from the `STO-Project/` directory with `PYTHONPATH` set to the project root (required because `main.py` imports `src.*` directly).

**Run the API server:**
```bash
PYTHONPATH=. uvicorn main:app --reload
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run all tests:**
```bash
PYTHONPATH=. pytest tests/ -v --tb=short
```

**Run a single test:**
```bash
PYTHONPATH=. pytest tests/test_main.py::test_create_client -v
```

**Build and run with Docker:**
```bash
docker build -t sto-service .
docker run -p 8000:8000 sto-service
```

**Enable test data seeding on startup:** create a `.env` file with `TEST_MODE=True`.

## Architecture

The app is a FastAPI service managing an auto service station (СТО) — clients and their vehicles.

**Request flow:** HTTP request → `main.py` router → `src/api/{clients,vehicles}.py` (FastAPI router) → `src/crud.py` (DB access) → SQLite via SQLAlchemy.

**Key design pattern — dual-purpose model files:** Each file in `src/models/` contains both the SQLAlchemy ORM class (e.g. `ClientModel`) and the Pydantic schemas (e.g. `Client`, `CreateClientRequest`) for that resource. The ORM class maps to a DB table; the Pydantic classes handle validation and serialization.

**`src/crud.py`** is the only place that touches the database. All functions accept a `Session` as their first argument and return Pydantic model instances (not ORM objects). API routers receive a DB session via `Depends(get_db)` and pass it directly to crud functions — no business logic lives in routers.

**Database:** SQLite file `sto_database.db` auto-created on first startup via `Base.metadata.create_all()` in the `lifespan` handler in `main.py`. IDs are UUIDs stored as strings in SQLite.

**Data model:** `Client` (1) → `Vehicle` (many). `Vehicle.owner_id` is a FK to `clients.id`. `vehicle_type` is a string enum: `'car'` or `'truck'`.

**Settings:** `config.py` uses `pydantic-settings` with `.env` file support. Settings are cached via `@lru_cache`. Currently: `APPLICATION_VERSION` and `TEST_MODE`.

**Tests** (`tests/test_main.py`): use `TestClient` (synchronous) with a separate `test_sto.db` SQLite file, overriding the `get_db` dependency. Each test function gets a fresh schema via the `autouse` `setup_db` fixture.

## CI/CD

GitHub Actions workflow (`.github/workflows/main.yml`) has 3 stages:
1. **pre-build** — calculates next semver by querying Docker Hub for latest published tag and incrementing PATCH.
2. **build-and-test** — installs deps, runs pytest, builds Docker image as smoke test. Runs on all branches.
3. **post-build** — pushes versioned and `latest` Docker images to Docker Hub. Runs **only on `main`**.

Requires GitHub secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`. Optional variable: `MANUALLY_SETUP_APP_VERSION` to override auto-versioning.
