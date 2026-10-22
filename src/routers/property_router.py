from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from typing import Optional

from src.dto.paginated_response import PaginatedResponseDTO
from src.dto.property_dto import PropertyDTO
from src.schemas.property_schema import PropertyCreateSchema, PropertyUpdateSchema
from src.controller.property_controller import PropertyController
from src.dependencies.authorization import require_master_user
from src.dependencies.property import get_property_controller

bearer_scheme = HTTPBearer()

property_router = APIRouter(
    prefix="/properties",
    tags=["4. Imóveis (Properties)"],
    dependencies=[Depends(bearer_scheme)]
)

@property_router.post("", response_model=PropertyDTO, status_code=status.HTTP_201_CREATED)
def create_property(
    schema: PropertyCreateSchema,
    controller: PropertyController = Depends(get_property_controller),
) -> PropertyDTO:
    return controller.create_property(schema)

@property_router.get("", response_model=PaginatedResponseDTO[PropertyDTO])
def list_properties(
    skip: int = 0, 
    limit: int = 10, 
    search_term: Optional[str] = None,
    property_name: Optional[str] = None,
    owner_name: Optional[str] = None,
    only_active_contracts: bool = False,
    controller: PropertyController = Depends(get_property_controller),
) -> PaginatedResponseDTO[PropertyDTO]:
    return controller.get_paginated_properties(skip, limit, search_term, property_name, owner_name, only_active_contracts)

@property_router.get("/{property_key}", response_model=PropertyDTO)
def get_property(
    property_key: str,
    controller: PropertyController = Depends(get_property_controller),
) -> PropertyDTO:
    return controller.get_property(property_key)

@property_router.put("/{property_key}", response_model=PropertyDTO)
def update_property(
    property_key: str,
    schema: PropertyUpdateSchema,
    controller: PropertyController = Depends(get_property_controller),
) -> PropertyDTO:
    return controller.update_property(property_key, schema)

@property_router.delete(
    "/{property_key}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_master_user)],
)
def delete_property(
    property_key: str,
    controller: PropertyController = Depends(get_property_controller),
) -> None:
    controller.delete_property(property_key)