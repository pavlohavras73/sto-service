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

**Request flow:** HTTP request → `main.py` router → `src/api/{clients,vehicles}.py` (FastAPI router) → `src/dependencies.py` (DI factory) → `ClientRepository`/`VehicleRepository` (PostgreSQL) or `ClientService`/`VehicleService` (in-memory cache).

**Storage abstraction pattern:**
- `src/services/client_storage.py` — abstract `ClientStorage` ABC
- `src/services/vehicle_storage.py` — abstract `VehicleStorage` ABC
- `src/services/client_service.py` — in-memory dict implementation (used when `TEST_MODE=True`)
- `src/services/vehicle_service.py` — in-memory dict implementation (used when `TEST_MODE=True`)
- `src/db/client_repository.py` — SQLAlchemy PostgreSQL implementation
- `src/db/vehicle_repository.py` — SQLAlchemy PostgreSQL implementation
- `src/dependencies.py` — DI factory: returns cache or DB implementation based on `TEST_MODE`

**Key design pattern — dual-purpose model files:** Each file in `src/models/` contains both the SQLAlchemy ORM class (e.g. `ClientModel`) and the Pydantic schemas (e.g. `Client`, `CreateClientRequest`). ORM models use `schema='sto_khnu'` for PostgreSQL.

**Database:** PostgreSQL via SQLAlchemy. Schema: `sto_khnu`. Migrations managed by **Alembic** — the web service does NOT apply migrations; the `sto-migration` Docker service handles that.

**Data model:** `Client` (1) → `Vehicle` (many). `Vehicle.owner_id` is a FK to `sto_khnu.clients.id`. `vehicle_type` is a string enum: `'car'` or `'truck'`.

**Settings:** `config.py` uses `pydantic-settings` with `.env` file support. Settings: `APPLICATION_VERSION`, `TEST_MODE`, `DATABASE_URL`.

**Tests** (`tests/test_main.py`): override `get_client_storage` and `get_vehicle_storage` DI to return fresh in-memory `ClientService`/`VehicleService` instances per test. No DB required.

**Migration job** (`migration/main.py`): standalone console app that runs `alembic upgrade head`. Built as separate Docker image `sto-migration`. Runs before `sto-service` via `depends_on: service_completed_successfully`.

## CI/CD

GitHub Actions workflow (`.github/workflows/main.yml`) has 3 stages:
1. **pre-build** — calculates next semver by querying Docker Hub for latest published tag and incrementing PATCH.
2. **build-and-test** — installs deps, runs pytest, builds Docker image as smoke test. Runs on all branches.
3. **post-build** — pushes versioned and `latest` Docker images to Docker Hub. Runs **only on `main`**.

Requires GitHub secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`. Optional variable: `MANUALLY_SETUP_APP_VERSION` to override auto-versioning.
