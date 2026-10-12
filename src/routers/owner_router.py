from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional

from src.database.config import get_db
from src.dto.owner_dto import OwnerDTO
from src.dto.paginated_response import PaginatedResponseDTO # Descomente se usar paginação
from src.schemas.owner_schema import OwnerCreateSchema, OwnerUpdateSchema
from src.controller.owner_controller import OwnerController
from src.dependencies.authorization import require_master_user

bearer_scheme = HTTPBearer()

owner_router = APIRouter(
    prefix="/owners",
    tags=["Proprietários (Owners)"],
    dependencies=[Depends(bearer_scheme)]
)

@owner_router.post("", response_model=OwnerDTO, status_code=status.HTTP_201_CREATED)
def create_owner(schema: OwnerCreateSchema, db: Session = Depends(get_db)):
    controller = OwnerController(db)
    return controller.create_owner(schema)

@owner_router.get("/{owner_key}", response_model=OwnerDTO)
def get_owner(owner_key: str, db: Session = Depends(get_db)):
    controller = OwnerController(db)
    return controller.get_owner(owner_key)

@owner_router.get("", response_model=PaginatedResponseDTO[OwnerDTO])
def list_owners(skip: int = 0, limit: int = 10, search_term: Optional[str] = None, db: Session = Depends(get_db)):
    controller = OwnerController(db)
    return controller.get_paginated_owners(skip, limit, search_term)

@owner_router.put("/{owner_key}", response_model=OwnerDTO)
def update_owner(owner_key: str, schema: OwnerUpdateSchema, db: Session = Depends(get_db)):
    controller = OwnerController(db)
    return controller.update_owner(owner_key, schema)

@owner_router.delete(
    "/{owner_key}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_master_user)],
)
def delete_owner(owner_key: str, db: Session = Depends(get_db)):
    controller = OwnerController(db)
    controller.delete_owner(owner_key)