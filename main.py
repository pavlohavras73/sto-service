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
    from src.database import SessionLocal
    from src.models.client import Client
    from src.models.vehicle import Vehicle
    import src.crud as crud

    db = SessionLocal()
    try:
        # Only seed if DB is empty
        if crud.get_clients(db):
            logger.info("DB already has data — skipping seed")
            return

        client1 = Client(name="Іван Петренко", phone="+380501234567")
        client2 = Client(name="Олена Коваль", phone="+380671234567")
        crud.create_client(db, client1)
        logger.info(f"Test client seeded: {client1.id} - {client1.name}")
        crud.create_client(db, client2)
        logger.info(f"Test client seeded: {client2.id} - {client2.name}")

        vehicle1 = Vehicle(brand="Toyota", plate="AA1234BB", vehicle_type="car", owner_id=client1.id)
        vehicle2 = Vehicle(brand="Volvo", plate="BB5678CC", vehicle_type="truck", owner_id=client1.id)
        vehicle3 = Vehicle(brand="Honda", plate="CC9012DD", vehicle_type="car", owner_id=client2.id)
        crud.create_vehicle(db, vehicle1)
        logger.info(f"Test vehicle seeded: {vehicle1.id} - {vehicle1.brand}")
        crud.create_vehicle(db, vehicle2)
        logger.info(f"Test vehicle seeded: {vehicle2.id} - {vehicle2.brand}")
        crud.create_vehicle(db, vehicle3)
        logger.info(f"Test vehicle seeded: {vehicle3.id} - {vehicle3.brand}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.database import engine, Base
    # Import models so SQLAlchemy registers them before create_all
    import src.models.client  # noqa: F401
    import src.models.vehicle  # noqa: F401

    logger.info("Creating database tables if not exist...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database ready: sto_database.db")

    settings = config.get_settings()
    logger.info(f"Starting STO Service API v{settings.APPLICATION_VERSION}")
    if settings.TEST_MODE:
        logger.info("TEST_MODE enabled — seeding test data...")
        _seed_test_data()
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
