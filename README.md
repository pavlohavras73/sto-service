# STO Service API

A RESTful API for managing an auto service station (СТО): clients and their vehicles.
Built with **FastAPI**, persisted with **SQLite** via **SQLAlchemy**, validated with **Pydantic**.

---

## Tech Stack

| Layer        | Technology                     |
|--------------|-------------------------------|
| Web framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM          | [SQLAlchemy 2.x](https://docs.sqlalchemy.org/) |
| Database     | SQLite (`sto_database.db`)     |
| Validation   | [Pydantic v2](https://docs.pydantic.dev/) |
| Settings     | pydantic-settings + `.env`     |
| Server       | Uvicorn (ASGI)                 |

---

## Requirements

- Python 3.10+
- pip packages: `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `pydantic-settings`

Install all dependencies:

```bash
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings
```

---

## Running the Application

```powershell
$env:PYTHONPATH="."; python -m uvicorn main:app --reload
```

The API will be available at:

- **Swagger UI** → http://127.0.0.1:8000/docs
- **ReDoc**       → http://127.0.0.1:8000/redoc
- **Root**        → http://127.0.0.1:8000/

### Optional: seed test data on startup

Create a `.env` file in the project root:

```env
TEST_MODE=True
```

This will insert two demo clients and three demo vehicles into the database on first launch.

---

## API Endpoints

### Clients

| Method | Endpoint                        | Description              |
|--------|---------------------------------|--------------------------|
| GET    | `/clients`                      | List all clients         |
| GET    | `/clients/{id}`                 | Get client by ID         |
| POST   | `/clients`                      | Create a new client      |
| PUT    | `/clients/{id}`                 | Update a client          |
| DELETE | `/clients/{id}`                 | Delete a client          |
| GET    | `/clients/{id}/vehicles`        | List vehicles of a client|

### Vehicles

| Method | Endpoint                        | Description              |
|--------|---------------------------------|--------------------------|
| GET    | `/vehicles`                     | List all vehicles        |
| GET    | `/vehicles/{id}`                | Get vehicle by ID        |
| POST   | `/vehicles`                     | Create a new vehicle     |
| PUT    | `/vehicles/{id}`                | Update a vehicle         |
| DELETE | `/vehicles/{id}`                | Delete a vehicle         |

---

## Project Structure

```
STO-Project/
├── main.py                  # Application entry point, lifespan, logging setup
├── config.py                # Settings (pydantic-settings, .env support)
├── sto_database.db          # SQLite database file (auto-created on first run)
├── app.log                  # Application log file (auto-created on first run)
│
└── src/
    ├── database.py          # SQLAlchemy engine, SessionLocal, Base, get_db()
    ├── crud.py              # CRUD functions (Create / Read / Update / Delete)
    │
    ├── models/              # Data models
    │   ├── client.py        # ClientModel (ORM) + Client, CreateClientRequest (Pydantic)
    │   └── vehicle.py       # VehicleModel (ORM) + Vehicle, CreateVehicleRequest (Pydantic)
    │
    ├── api/                 # FastAPI routers
    │   ├── clients.py       # /clients endpoints
    │   └── vehicles.py      # /vehicles endpoints
    │
    └── middlewares/
        └── error_handler.py # Global exception middleware (500 handler)
```

### Key folders explained

| Path              | Purpose |
|-------------------|---------|
| `src/api/`        | FastAPI `APIRouter` definitions — one file per resource. Routers receive a DB session via `Depends(get_db)` and delegate all business logic to `crud.py`. |
| `src/models/`     | Each file contains both the **SQLAlchemy ORM class** (mapped to a DB table) and the **Pydantic schemas** (used for request body validation and response serialization). |
| `src/database.py` | Single source of truth for the database connection: creates the engine, exposes `SessionLocal`, defines `Base`, and provides the `get_db` dependency generator. |
| `src/crud.py`     | Pure data-access functions that take a `Session` as the first argument. No HTTP logic here — just DB queries. |
| `src/middlewares/`| Starlette middleware classes. Currently handles unhandled exceptions and returns a structured JSON 500 response. |

---

## Logging

All events are written simultaneously to:

- **stdout** (console) — visible during development
- **`app.log`** (file) — persists across restarts

Logged events include: server startup/shutdown, client/vehicle creation and deletion, 404 warnings.

Log format:
```
[2026-03-08 15:00:00,123] [INFO] src.crud: New client added to DB: <uuid> - Іван Петренко
```

---

## Data Model

```
Client (1) ──────< Vehicle (Many)
  id (UUID/PK)       id (UUID/PK)
  name               brand
  phone              plate
                     vehicle_type  ('car' | 'truck')
                     owner_id (FK → clients.id)
```

---

## Git Repository

[https://github.com/pavlohavras73/sto-service](https://github.com/pavlohavras73/sto-service)
