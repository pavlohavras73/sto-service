import logging
from uuid import UUID, uuid4
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.client import ClientModel, Client
from src.services.client_storage import ClientStorage

logger = logging.getLogger(__name__)


class ClientRepository(ClientStorage):
    """Database-backed implementation of ClientStorage using SQLAlchemy."""

    def __init__(self, db: Session):
        self.db = db

    def create_client(self, client: Client) -> Client:
        db_client = ClientModel(id=str(client.id), name=client.name, phone=client.phone)
        self.db.add(db_client)
        self.db.commit()
        self.db.refresh(db_client)
        logger.info(f"[db] Client created: {db_client.id} - {db_client.name}")
        return Client(id=db_client.id, name=db_client.name, phone=db_client.phone)

    def get_client(self, client_id: UUID) -> Optional[Client]:
        row = self.db.query(ClientModel).filter(ClientModel.id == str(client_id)).first()
        if row:
            return Client(id=row.id, name=row.name, phone=row.phone)
        return None

    def get_clients(self) -> List[Client]:
        rows = self.db.query(ClientModel).all()
        return [Client(id=r.id, name=r.name, phone=r.phone) for r in rows]

    def update_client(self, client_id: UUID, updated: Client) -> Optional[Client]:
        row = self.db.query(ClientModel).filter(ClientModel.id == str(client_id)).first()
        if not row:
            return None
        row.name = updated.name
        row.phone = updated.phone
        self.db.commit()
        self.db.refresh(row)
        logger.info(f"[db] Client updated: {client_id}")
        return Client(id=row.id, name=row.name, phone=row.phone)

    def delete_client(self, client_id: UUID) -> bool:
        row = self.db.query(ClientModel).filter(ClientModel.id == str(client_id)).first()
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        logger.info(f"[db] Client deleted: {client_id}")
        return True
