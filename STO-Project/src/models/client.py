import logging
from uuid import UUID, uuid4
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Column, String

from src.database import Base

logger = logging.getLogger(__name__)


# --- SQLAlchemy ORM model ---

class ClientModel(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)


# --- Pydantic schemas ---

class CreateClientRequest(BaseModel):
    name: str
    phone: str

    @field_validator("name", "phone")
    @classmethod
    def must_not_be_empty(cls, v, info):
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return v


class Client(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    phone: str

    model_config = {"from_attributes": True}
