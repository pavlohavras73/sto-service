import logging
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from src.models.client import Client, CreateClientRequest
from src.models.vehicle import Vehicle
from src.services.client_storage import ClientStorage
from src.services.vehicle_storage import VehicleStorage
from src.dependencies import get_client_storage, get_vehicle_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get(
    "",
    response_model=List[Client],
    summary="Get all clients",
    description="Returns a list of all registered clients in the system.",
)
def get_clients(storage: ClientStorage = Depends(get_client_storage)):
    return storage.get_clients()


@router.get(
    "/{client_id}",
    response_model=Client,
    summary="Get client by ID",
    description="Returns a single client by their UUID. Returns 404 if the client does not exist.",
)
def get_client(client_id: UUID, storage: ClientStorage = Depends(get_client_storage)):
    client = storage.get_client(client_id)
    if not client:
        logger.warning(f"Client {client_id} not found")
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
    return client


@router.post(
    "",
    response_model=Client,
    status_code=201,
    summary="Create a new client",
    description="Creates a new client with the provided name and phone number. Returns the created client with a generated UUID.",
)
def create_client(request: CreateClientRequest, storage: ClientStorage = Depends(get_client_storage)):
    client = Client(name=request.name, phone=request.phone)
    logger.info(f"Creating client: {client.id} - {client.name}")
    return storage.create_client(client)


@router.put(
    "/{client_id}",
    response_model=Client,
    summary="Update a client",
    description="Updates the name and phone of an existing client identified by UUID. Returns 404 if not found.",
)
def update_client(client_id: UUID, request: CreateClientRequest, storage: ClientStorage = Depends(get_client_storage)):
    if not storage.get_client(client_id):
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
    updated = Client(id=client_id, name=request.name, phone=request.phone)
    return storage.update_client(client_id, updated)


@router.delete(
    "/{client_id}",
    status_code=204,
    summary="Delete a client",
    description="Deletes a client by UUID. Also removes all associated vehicles. Returns 404 if not found.",
)
def delete_client(client_id: UUID, storage: ClientStorage = Depends(get_client_storage)):
    if not storage.delete_client(client_id):
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")


@router.get(
    "/{client_id}/vehicles",
    response_model=List[Vehicle],
    summary="Get all vehicles for a client",
    description="Returns a list of all vehicles registered under the given client. Returns 404 if the client does not exist.",
)
def get_client_vehicles(
    client_id: UUID,
    client_storage: ClientStorage = Depends(get_client_storage),
    vehicle_storage: VehicleStorage = Depends(get_vehicle_storage),
):
    if not client_storage.get_client(client_id):
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
    return vehicle_storage.get_vehicles_by_client(client_id)
