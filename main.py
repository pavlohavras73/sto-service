import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

import config
from src.api import clients, vehicles
from src.middlewares.error_handler import ErrorHandlerMiddleware

# ── Logging setup ─────────────────────────────────────────────────────────────
_fmt = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=_fmt,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ── OpenAPI tags ──────────────────────────────────────────────────────────────
tags_metadata = [
    {
        "name": "clients",
        "description": "Operations with clients.",
    },
    {
        "name": "vehicles",
        "description": "Operations with vehicles. A client can have many vehicles (One-to-Many).",
    },
]


def _seed_test_data() -> None:
    """Seed in-memory storage with test data when TEST_MODE=True."""
    from src.dependencies import get_client_storage, get_vehicle_storage
    from src.models.client import Client
    from src.models.vehicle import Vehicle

    # Get the singleton in-memory instances
    client_storage = next(iter([s for s in [get_client_storage.__wrapped__ if hasattr(get_client_storage, '__wrapped__') else None] if s]), None)

    # Access singleton services directly
    from src.dependencies import _client_service, _vehicle_service

    if _client_service.get_clients():
        logger.info("In-memory storage already has data — skipping seed")
        return

    client1 = Client(name="Іван Петренко", phone="+380501234567")
    client2 = Client(name="Олена Коваль", phone="+380671234567")
    _client_service.create_client(client1)
    _client_service.create_client(client2)
    logger.info(f"Test clients seeded: {client1.id}, {client2.id}")

    vehicle1 = Vehicle(brand="Toyota", plate="AA1234BB", vehicle_type="car", owner_id=client1.id)
    vehicle2 = Vehicle(brand="Volvo", plate="BB5678CC", vehicle_type="truck", owner_id=client1.id)
    vehicle3 = Vehicle(brand="Honda", plate="CC9012DD", vehicle_type="car", owner_id=client2.id)
    _vehicle_service.create_vehicle(vehicle1)
    _vehicle_service.create_vehicle(vehicle2)
    _vehicle_service.create_vehicle(vehicle3)
    logger.info(f"Test vehicles seeded: {vehicle1.id}, {vehicle2.id}, {vehicle3.id}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import models so SQLAlchemy registers them (needed for Alembic introspection)
    import src.models.client  # noqa: F401
    import src.models.vehicle  # noqa: F401

    settings = config.get_settings()
    logger.info(f"Starting STO Service API v{settings.APPLICATION_VERSION}")

    if settings.TEST_MODE:
        logger.info("TEST_MODE enabled — using in-memory storage, seeding test data...")
        _seed_test_data()
    else:
        logger.info("Production mode — using PostgreSQL database (migrations managed by migration job)")

    yield
    logger.info("Shutting down STO Service API")


app = FastAPI(
    title="STO Service API",
    description="API for managing STO clients and their vehicles",
    version=config.get_settings().APPLICATION_VERSION,
    contact={
        "name": "STO Service",
        "email": "sto@example.com",
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.add_middleware(ErrorHandlerMiddleware)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


app.include_router(clients.router)
app.include_router(vehicles.router)


@app.get("/", tags=["info"])
def read_root():
    settings = config.get_settings()
    return {"status": "STO API is running", "version": settings.APPLICATION_VERSION}


@app.get("/info", tags=["info"], summary="Get application info")
def info(settings: Annotated[config.Settings, Depends(config.get_settings)]):
    return {"appVersion": settings.APPLICATION_VERSION}
