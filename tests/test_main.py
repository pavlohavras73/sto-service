"""
Tests use in-memory storage (ClientService / VehicleService) by overriding DI.
This avoids DB/schema issues and keeps tests fast and self-contained.
"""
import pytest
from fastapi.testclient import TestClient

from src.dependencies import get_client_storage, get_vehicle_storage
from src.services.client_service import ClientService
from src.services.vehicle_service import VehicleService
from main import app

# Per-test fresh in-memory storage instances
_client_storage: ClientService
_vehicle_storage: VehicleService


def override_get_client_storage():
    return _client_storage


def override_get_vehicle_storage():
    return _vehicle_storage


app.dependency_overrides[get_client_storage] = override_get_client_storage
app.dependency_overrides[get_vehicle_storage] = override_get_vehicle_storage


@pytest.fixture(autouse=True)
def fresh_storage():
    """Reset in-memory storage before each test."""
    global _client_storage, _vehicle_storage
    _client_storage = ClientService()
    _vehicle_storage = VehicleService()
    yield


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
    assert len(response.json()) == 0


def test_create_and_get_client():
    client.post("/clients/", json={"name": "Anna", "phone": "+380501111111"})
    response = client.get("/clients/")
    assert response.status_code == 200
    names = [c["name"] for c in response.json()]
    assert "Anna" in names


def test_get_nonexistent_client():
    response = client.get("/clients/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_client():
    create_resp = client.post("/clients/", json={"name": "Old Name", "phone": "+380501111111"})
    client_id = create_resp.json()["id"]

    update_resp = client.put(f"/clients/{client_id}", json={"name": "New Name", "phone": "+380502222222"})
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "New Name"


def test_delete_client():
    create_resp = client.post("/clients/", json={"name": "To Delete", "phone": "+380503333333"})
    client_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/clients/{client_id}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/clients/{client_id}")
    assert get_resp.status_code == 404


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


def test_create_vehicle_unknown_client():
    response = client.post(
        "/vehicles/",
        json={"brand": "BMW", "plate": "AA0001BB", "vehicle_type": "car", "owner_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 404


def test_get_vehicles_empty():
    response = client.get("/vehicles/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


def test_get_client_vehicles():
    create_resp = client.post("/clients/", json={"name": "Alice", "phone": "+380504444444"})
    owner_id = create_resp.json()["id"]

    client.post("/vehicles/", json={"brand": "Toyota", "plate": "TT1234AA", "vehicle_type": "car", "owner_id": owner_id})
    client.post("/vehicles/", json={"brand": "Volvo", "plate": "VV5678BB", "vehicle_type": "truck", "owner_id": owner_id})

    response = client.get(f"/clients/{owner_id}/vehicles")
    assert response.status_code == 200
    assert len(response.json()) == 2
