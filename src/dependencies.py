from fastapi import Depends
from sqlalchemy.orm import Session

from config import get_settings
from src.database import get_db
from src.services.client_storage import ClientStorage
from src.services.vehicle_storage import VehicleStorage
from src.services.client_service import ClientService
from src.services.vehicle_service import VehicleService
from src.db.client_repository import ClientRepository
from src.db.vehicle_repository import VehicleRepository

# Singleton in-memory instances (used only when TEST_MODE=True)
_client_service = ClientService()
_vehicle_service = VehicleService()


def get_client_storage(db: Session = Depends(get_db)) -> ClientStorage:
    """Returns ClientService (in-memory) when TEST_MODE=True, else ClientRepository (DB)."""
    if get_settings().TEST_MODE:
        return _client_service
    return ClientRepository(db)


def get_vehicle_storage(db: Session = Depends(get_db)) -> VehicleStorage:
    """Returns VehicleService (in-memory) when TEST_MODE=True, else VehicleRepository (DB)."""
    if get_settings().TEST_MODE:
        return _vehicle_service
    return VehicleRepository(db)
