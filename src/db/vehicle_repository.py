import logging
from uuid import UUID
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.vehicle import VehicleModel, Vehicle
from src.services.vehicle_storage import VehicleStorage

logger = logging.getLogger(__name__)


class VehicleRepository(VehicleStorage):
    """Database-backed implementation of VehicleStorage using SQLAlchemy."""

    def __init__(self, db: Session):
        self.db = db

    def create_vehicle(self, vehicle: Vehicle) -> Vehicle:
        db_vehicle = VehicleModel(
            id=str(vehicle.id),
            brand=vehicle.brand,
            plate=vehicle.plate,
            vehicle_type=vehicle.vehicle_type,
            owner_id=str(vehicle.owner_id),
        )
        self.db.add(db_vehicle)
        self.db.commit()
        self.db.refresh(db_vehicle)
        logger.info(f"[db] Vehicle created: {db_vehicle.id} ({db_vehicle.brand}) for client: {db_vehicle.owner_id}")
        return self._to_model(db_vehicle)

    def get_vehicle(self, vehicle_id: UUID) -> Optional[Vehicle]:
        row = self.db.query(VehicleModel).filter(VehicleModel.id == str(vehicle_id)).first()
        return self._to_model(row) if row else None

    def get_vehicles(self) -> List[Vehicle]:
        rows = self.db.query(VehicleModel).all()
        return [self._to_model(r) for r in rows]

    def get_vehicles_by_client(self, client_id: UUID) -> List[Vehicle]:
        rows = self.db.query(VehicleModel).filter(VehicleModel.owner_id == str(client_id)).all()
        return [self._to_model(r) for r in rows]

    def update_vehicle(self, vehicle_id: UUID, updated: Vehicle) -> Optional[Vehicle]:
        row = self.db.query(VehicleModel).filter(VehicleModel.id == str(vehicle_id)).first()
        if not row:
            return None
        row.brand = updated.brand
        row.plate = updated.plate
        row.vehicle_type = updated.vehicle_type
        row.owner_id = str(updated.owner_id)
        self.db.commit()
        self.db.refresh(row)
        logger.info(f"[db] Vehicle updated: {vehicle_id}")
        return self._to_model(row)

    def delete_vehicle(self, vehicle_id: UUID) -> bool:
        row = self.db.query(VehicleModel).filter(VehicleModel.id == str(vehicle_id)).first()
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        logger.info(f"[db] Vehicle deleted: {vehicle_id}")
        return True

    @staticmethod
    def _to_model(row: VehicleModel) -> Vehicle:
        return Vehicle(
            id=row.id,
            brand=row.brand,
            plate=row.plate,
            vehicle_type=row.vehicle_type,
            owner_id=row.owner_id,
        )
