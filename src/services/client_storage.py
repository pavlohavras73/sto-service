from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional

from src.models.client import Client


class ClientStorage(ABC):
    """Abstract base class for client storage (in-memory cache or database)."""

    @abstractmethod
    def create_client(self, client: Client) -> Client:
        pass

    @abstractmethod
    def get_client(self, client_id: UUID) -> Optional[Client]:
        pass

    @abstractmethod
    def get_clients(self) -> List[Client]:
        pass

    @abstractmethod
    def update_client(self, client_id: UUID, updated: Client) -> Optional[Client]:
        pass

    @abstractmethod
    def delete_client(self, client_id: UUID) -> bool:
        pass
