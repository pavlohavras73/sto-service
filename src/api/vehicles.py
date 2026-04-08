import logging
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from src.models.vehicle import Vehicle, CreateVehicleRequest
from src.services.client_storage import ClientStorage
from src.services.vehicle_storage import VehicleStorage
from src.dependencies import get_client_storage, get_vehicle_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get(
    "",
    response_model=List[Vehicle],
    summary="Get all vehicles",
    description="Returns a list of all vehicles registered in the system across all clients.",
)
def get_vehicles(storage: VehicleStorage = Depends(get_vehicle_storage)):
    return storage.get_vehicles()


@router.get(
    "/{vehicle_id}",
    response_model=Vehicle,
    summary="Get vehicle by ID",
    description="Returns a single vehicle by its UUID. Returns 404 if the vehicle does not exist.",
)
def get_vehicle(vehicle_id: UUID, storage: VehicleStorage = Depends(get_vehicle_storage)):
    vehicle = storage.get_vehicle(vehicle_id)
    if not vehicle:
        logger.warning(f"Vehicle {vehicle_id} not found")
        raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")
    return vehicle


@router.post(
    "",
    response_model=Vehicle,
    status_code=201,
    summary="Create a new vehicle",
    description=(
        "Registers a new vehicle for an existing client. "
        "The `vehicle_type` field must be either `car` or `truck`. "
        "Returns 404 if the specified owner (client) does not exist."
    ),
)
def create_vehicle(
    request: CreateVehicleRequest,
    client_storage: ClientStorage = Depends(get_client_storage),
    vehicle_storage: VehicleStorage = Depends(get_vehicle_storage),
):
    if not client_storage.get_client(request.owner_id):
        raise HTTPException(status_code=404, detail=f"Client {request.owner_id} not found")
    vehicle = Vehicle(
        brand=request.brand,
        plate=request.plate,
        vehicle_type=request.vehicle_type,
        owner_id=request.owner_id,
    )
    logger.info(f"Creating vehicle: {vehicle.id} ({vehicle.brand}) for client: {vehicle.owner_id}")
    return vehicle_storage.create_vehicle(vehicle)


@router.put(
    "/{vehicle_id}",
    response_model=Vehicle,
    summary="Update a vehicle",
    description="Updates brand, plate, type, and owner of an existing vehicle by UUID. Returns 404 if vehicle or new owner not found.",
)
def update_vehicle(
    vehicle_id: UUID,
    request: CreateVehicleRequest,
    client_storage: ClientStorage = Depends(get_client_storage),
    vehicle_storage: VehicleStorage = Depends(get_vehicle_storage),
):
    if not vehicle_storage.get_vehicle(vehicle_id):
        raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")
    if not client_storage.get_client(request.owner_id):
        raise HTTPException(status_code=404, detail=f"Client {request.owner_id} not found")
    updated = Vehicle(
        id=vehicle_id,
        brand=request.brand,
        plate=request.plate,
        vehicle_type=request.vehicle_type,
        owner_id=request.owner_id,
    )
    return vehicle_storage.update_vehicle(vehicle_id, updated)


@router.delete(
    "/{vehicle_id}",
    status_code=204,
    summary="Delete a vehicle",
    description="Deletes a vehicle by UUID. Returns 404 if the vehicle does not exist.",
)
def delete_vehicle(vehicle_id: UUID, storage: VehicleStorage = Depends(get_vehicle_storage)):
    if not storage.delete_vehicle(vehicle_id):
        raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")
