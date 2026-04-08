import logging
from uuid import UUID
from typing import List, Optional

from src.models.client import Client
from src.services.client_storage import ClientStorage

logger = logging.getLogger(__name__)


class ClientService(ClientStorage):
    """In-memory (cache) implementation of ClientStorage. Used when TEST_MODE=True."""

    def __init__(self):
        self._clients: dict[UUID, Client] = {}

    def create_client(self, client: Client) -> Client:
        self._clients[client.id] = client
        logger.info(f"[cache] Client created: {client.id} - {client.name}")
        return client

    def get_client(self, client_id: UUID) -> Optional[Client]:
        return self._clients.get(client_id)

    def get_clients(self) -> List[Client]:
        return list(self._clients.values())

    def update_client(self, client_id: UUID, updated: Client) -> Optional[Client]:
        if client_id not in self._clients:
            return None
        self._clients[client_id] = updated
        logger.info(f"[cache] Client updated: {client_id}")
        return updated

    def delete_client(self, client_id: UUID) -> bool:
        if client_id not in self._clients:
            return False
        del self._clients[client_id]
        logger.info(f"[cache] Client deleted: {client_id}")
        return True
