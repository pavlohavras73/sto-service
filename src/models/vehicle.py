import logging
from uuid import UUID, uuid4
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Column, String, ForeignKey

from src.database import Base

logger = logging.getLogger(__name__)


# --- SQLAlchemy ORM model ---

class VehicleModel(Base):
    __tablename__ = "vehicles"

    id = Column(String, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    plate = Column(String, nullable=False)
    vehicle_type = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("clients.id"), nullable=False)


# --- Pydantic schemas ---

class CreateVehicleRequest(BaseModel):
    brand: str
    plate: str
    vehicle_type: str  # 'car' or 'truck'
    owner_id: UUID

    @field_validator("brand", "plate", "vehicle_type")
    @classmethod
    def must_not_be_empty(cls, v, info):
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return v


class Vehicle(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    brand: str
    plate: str
    vehicle_type: str  # 'car' or 'truck'
    owner_id: UUID

    model_config = {"from_attributes": True}
