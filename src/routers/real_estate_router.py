from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from src.database.config import get_db
from typing import Optional

from src.dto.paginated_response import PaginatedResponseDTO
from src.dto.real_estate_dto import RealEstateDTO
from src.schemas.real_estate_schema import RealEstateCreateSchema, RealEstateUpdateSchema
from src.controller.real_estate_controller import RealEstateController

bearer_scheme = HTTPBearer()

real_estate_router = APIRouter(
    prefix="/real-estates",
    tags=["5. Imobiliárias (Real Estates)"],
    dependencies=[Depends(bearer_scheme)]
)

@real_estate_router.post("", response_model=RealEstateDTO, status_code=status.HTTP_201_CREATED)
def create_real_estate(schema: RealEstateCreateSchema, db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    return controller.create_real_estate(schema)

@real_estate_router.get("", response_model=PaginatedResponseDTO[RealEstateDTO])
def list_real_estates(
    skip: int = 0, 
    limit: int = 10, 
    search_term: Optional[str] = None,
    name: Optional[str] = None,
    cnpj: Optional[str] = None,
    only_active_contracts: bool = False,
    db: Session = Depends(get_db)
):
    controller = RealEstateController(db)
    return controller.get_paginated_real_estates(skip, limit, search_term, name, cnpj, only_active_contracts)

@real_estate_router.get("/{real_estate_key}", response_model=RealEstateDTO)
def get_real_estate(real_estate_key: str, db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    return controller.get_real_estate(real_estate_key)

@real_estate_router.put("/{real_estate_key}", response_model=RealEstateDTO)
def update_real_estate(real_estate_key: str, schema: RealEstateUpdateSchema, db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    return controller.update_real_estate(real_estate_key, schema)

@real_estate_router.delete("/{real_estate_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_real_estate(real_estate_key: str, db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    controller.delete_real_estate(real_estate_key)