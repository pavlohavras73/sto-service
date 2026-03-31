import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base, get_db
from main import app

# Use an in-memory SQLite DB for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_sto.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    import src.models.client  # noqa: F401
    import src.models.vehicle  # noqa: F401
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_root_returns_status():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "STO API is running"
    assert "version" in data


def test_info_returns_version():
    response = client.get("/info")
    assert response.status_code == 200
    assert "appVersion" in response.json()


def test_create_client():
    response = client.post("/clients/", json={"name": "Test User", "phone": "+380991234567"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["phone"] == "+380991234567"
    assert "id" in data


def test_get_clients_empty():
    response = client.get("/clients/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_and_get_client():
    client.post("/clients/", json={"name": "Anna", "phone": "+380501111111"})
    response = client.get("/clients/")
    assert response.status_code == 200
    names = [c["name"] for c in response.json()]
    assert "Anna" in names


def test_get_nonexistent_client():
    response = client.get("/clients/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_vehicle_for_client():
    create_resp = client.post("/clients/", json={"name": "Bob", "phone": "+380502222222"})
    owner_id = create_resp.json()["id"]

    vehicle_resp = client.post(
        "/vehicles/",
        json={"brand": "BMW", "plate": "AA0001BB", "vehicle_type": "car", "owner_id": owner_id},
    )
    assert vehicle_resp.status_code == 201
    data = vehicle_resp.json()
    assert data["brand"] == "BMW"
    assert data["owner_id"] == owner_id


def test_get_vehicles_empty():
    response = client.get("/vehicles/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
