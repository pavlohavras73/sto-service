from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional

from src.models.vehicle import Vehicle


class VehicleStorage(ABC):
    """Abstract base class for vehicle storage (in-memory cache or database)."""

    @abstractmethod
    def create_vehicle(self, vehicle: Vehicle) -> Vehicle:
        pass

    @abstractmethod
    def get_vehicle(self, vehicle_id: UUID) -> Optional[Vehicle]:
        pass

    @abstractmethod
    def get_vehicles(self) -> List[Vehicle]:
        pass

    @abstractmethod
    def get_vehicles_by_client(self, client_id: UUID) -> List[Vehicle]:
        pass

    @abstractmethod
    def update_vehicle(self, vehicle_id: UUID, updated: Vehicle) -> Optional[Vehicle]:
        pass

    @abstractmethod
    def delete_vehicle(self, vehicle_id: UUID) -> bool:
        pass
