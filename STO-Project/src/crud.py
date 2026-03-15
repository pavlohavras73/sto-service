import logging
from uuid import UUID
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.client import ClientModel, Client
from src.models.vehicle import VehicleModel, Vehicle

logger = logging.getLogger(__name__)


# ── Clients ──────────────────────────────────────────────────────────────────

def get_clients(db: Session) -> List[Client]:
    rows = db.query(ClientModel).all()
    return [Client(id=r.id, name=r.name, phone=r.phone) for r in rows]


def get_client(db: Session, client_id: UUID) -> Optional[Client]:
    row = db.query(ClientModel).filter(ClientModel.id == str(client_id)).first()
    if row:
        return Client(id=row.id, name=row.name, phone=row.phone)
    return None


def create_client(db: Session, client: Client) -> Client:
    db_client = ClientModel(id=str(client.id), name=client.name, phone=client.phone)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    logger.info(f"New client added to DB: {db_client.id} - {db_client.name}")
    return client


def update_client(db: Session, client_id: UUID, updated: Client) -> Optional[Client]:
    row = db.query(ClientModel).filter(ClientModel.id == str(client_id)).first()
    if not row:
        return None
    row.name = updated.name
    row.phone = updated.phone
    db.commit()
    db.refresh(row)
    return Client(id=row.id, name=row.name, phone=row.phone)


def delete_client(db: Session, client_id: UUID) -> bool:
    row = db.query(ClientModel).filter(ClientModel.id == str(client_id)).first()
    if not row:
        return False
    db.delete(row)
    db.commit()
    logger.info(f"Client deleted from DB: {client_id}")
    return True


# ── Vehicles ─────────────────────────────────────────────────────────────────

def _row_to_vehicle(row: VehicleModel) -> Vehicle:
    return Vehicle(
        id=row.id,
        brand=row.brand,
        plate=row.plate,
        vehicle_type=row.vehicle_type,
        owner_id=row.owner_id,
    )


def get_vehicles(db: Session) -> List[Vehicle]:
    rows = db.query(VehicleModel).all()
    return [_row_to_vehicle(r) for r in rows]


def get_vehicle(db: Session, vehicle_id: UUID) -> Optional[Vehicle]:
    row = db.query(VehicleModel).filter(VehicleModel.id == str(vehicle_id)).first()
    return _row_to_vehicle(row) if row else None


def get_vehicles_by_client(db: Session, client_id: UUID) -> List[Vehicle]:
    rows = db.query(VehicleModel).filter(VehicleModel.owner_id == str(client_id)).all()
    return [_row_to_vehicle(r) for r in rows]


def create_vehicle(db: Session, vehicle: Vehicle) -> Vehicle:
    db_vehicle = VehicleModel(
        id=str(vehicle.id),
        brand=vehicle.brand,
        plate=vehicle.plate,
        vehicle_type=vehicle.vehicle_type,
        owner_id=str(vehicle.owner_id),
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    logger.info(f"New vehicle added to DB: {db_vehicle.id} ({db_vehicle.brand}) for client: {db_vehicle.owner_id}")
    return vehicle


def update_vehicle(db: Session, vehicle_id: UUID, updated: Vehicle) -> Optional[Vehicle]:
    row = db.query(VehicleModel).filter(VehicleModel.id == str(vehicle_id)).first()
    if not row:
        return None
    row.brand = updated.brand
    row.plate = updated.plate
    row.vehicle_type = updated.vehicle_type
    row.owner_id = str(updated.owner_id)
    db.commit()
    db.refresh(row)
    return _row_to_vehicle(row)


def delete_vehicle(db: Session, vehicle_id: UUID) -> bool:
    row = db.query(VehicleModel).filter(VehicleModel.id == str(vehicle_id)).first()
    if not row:
        return False
    db.delete(row)
    db.commit()
    logger.info(f"Vehicle deleted from DB: {vehicle_id}")
    return True
