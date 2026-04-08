import logging
from uuid import UUID
from typing import List, Optional

from src.models.vehicle import Vehicle
from src.services.vehicle_storage import VehicleStorage

logger = logging.getLogger(__name__)


class VehicleService(VehicleStorage):
    """In-memory (cache) implementation of VehicleStorage. Used when TEST_MODE=True."""

    def __init__(self):
        self._vehicles: dict[UUID, Vehicle] = {}

    def create_vehicle(self, vehicle: Vehicle) -> Vehicle:
        self._vehicles[vehicle.id] = vehicle
        logger.info(f"[cache] Vehicle created: {vehicle.id} - {vehicle.brand}")
        return vehicle

    def get_vehicle(self, vehicle_id: UUID) -> Optional[Vehicle]:
        return self._vehicles.get(vehicle_id)

    def get_vehicles(self) -> List[Vehicle]:
        return list(self._vehicles.values())

    def get_vehicles_by_client(self, client_id: UUID) -> List[Vehicle]:
        return [v for v in self._vehicles.values() if v.owner_id == client_id]

    def update_vehicle(self, vehicle_id: UUID, updated: Vehicle) -> Optional[Vehicle]:
        if vehicle_id not in self._vehicles:
            return None
        self._vehicles[vehicle_id] = updated
        logger.info(f"[cache] Vehicle updated: {vehicle_id}")
        return updated

    def delete_vehicle(self, vehicle_id: UUID) -> bool:
        if vehicle_id not in self._vehicles:
            return False
        del self._vehicles[vehicle_id]
        logger.info(f"[cache] Vehicle deleted: {vehicle_id}")
        return True
