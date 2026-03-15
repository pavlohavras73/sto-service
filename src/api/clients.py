import logging
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.client import Client, CreateClientRequest
from src.models.vehicle import Vehicle
import src.crud as crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=List[Client], summary="Get all clients")
def get_clients(db: Session = Depends(get_db)):
    return crud.get_clients(db)


@router.get("/{client_id}", response_model=Client, summary="Get client by ID")
def get_client(client_id: UUID, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id)
    if not client:
        logger.warning(f"Client {client_id} not found")
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
    return client


@router.post("", response_model=Client, status_code=201, summary="Create a new client")
def create_client(request: CreateClientRequest, db: Session = Depends(get_db)):
    client = Client(name=request.name, phone=request.phone)
    logger.info(f"Creating client: {client.id} - {client.name}")
    return crud.create_client(db, client)


@router.put("/{client_id}", response_model=Client, summary="Update a client")
def update_client(client_id: UUID, request: CreateClientRequest, db: Session = Depends(get_db)):
    if not crud.get_client(db, client_id):
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
    updated = Client(id=client_id, name=request.name, phone=request.phone)
    return crud.update_client(db, client_id, updated)


@router.delete("/{client_id}", status_code=204, summary="Delete a client")
def delete_client(client_id: UUID, db: Session = Depends(get_db)):
    if not crud.delete_client(db, client_id):
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")


@router.get("/{client_id}/vehicles", response_model=List[Vehicle], summary="Get all vehicles for a client")
def get_client_vehicles(client_id: UUID, db: Session = Depends(get_db)):
    if not crud.get_client(db, client_id):
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
    return crud.get_vehicles_by_client(db, client_id)
