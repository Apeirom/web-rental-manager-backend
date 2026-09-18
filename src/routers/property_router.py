from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from src.database.config import get_db
from typing import Optional

from src.dto.paginated_response import PaginatedResponseDTO
from src.dto.property_dto import PropertyDTO
from src.schemas.property_schema import PropertyCreateSchema, PropertyUpdateSchema
from src.controller.property_controller import PropertyController

bearer_scheme = HTTPBearer()

property_router = APIRouter(
    prefix="/properties",
    tags=["4. Imóveis (Properties)"],
    dependencies=[Depends(bearer_scheme)]
)

@property_router.post("", response_model=PropertyDTO, status_code=status.HTTP_201_CREATED)
def create_property(schema: PropertyCreateSchema, db: Session = Depends(get_db)):
    controller = PropertyController(db)
    return controller.create_property(schema)

@property_router.get("", response_model=PaginatedResponseDTO[PropertyDTO])
def list_properties(
    skip: int = 0, 
    limit: int = 10, 
    search_term: Optional[str] = None,
    property_name: Optional[str] = None,
    owner_name: Optional[str] = None,
    only_active_contracts: bool = False,
    db: Session = Depends(get_db)
):
    controller = PropertyController(db)
    return controller.get_paginated_properties(skip, limit, search_term, property_name, owner_name, only_active_contracts)

@property_router.get("/{property_key}", response_model=PropertyDTO)
def get_property(property_key: str, db: Session = Depends(get_db)):
    controller = PropertyController(db)
    return controller.get_property(property_key)

@property_router.put("/{property_key}", response_model=PropertyDTO)
def update_property(property_key: str, schema: PropertyUpdateSchema, db: Session = Depends(get_db)):
    controller = PropertyController(db)
    return controller.update_property(property_key, schema)

@property_router.delete("/{property_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(property_key: str, db: Session = Depends(get_db)):
    controller = PropertyController(db)
    controller.delete_property(property_key)