from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from src.database.config import get_db
from typing import Optional, Union

from src.dto.paginated_response import PaginatedResponseDTO
from src.dto.guarantee_dto import DepositDTO, GuarantorDTO, BailInsuranceDTO
from src.schemas.guarantee_schema import GuaranteeSchema
from src.controller.guarantee_controller import GuaranteeController

bearer_scheme = HTTPBearer()

guarantee_router = APIRouter(
    prefix="/guarantees",
    tags=["6. Garantias (Guarantees)"],
    dependencies=[Depends(bearer_scheme)]
)

@guarantee_router.post("", response_model=Union[GuarantorDTO, DepositDTO, BailInsuranceDTO], status_code=status.HTTP_201_CREATED)
def create_guarantee(schema: GuaranteeSchema, db: Session = Depends(get_db)):
    return GuaranteeController(db).create_guarantee(schema)

@guarantee_router.get("", response_model=PaginatedResponseDTO[Union[GuarantorDTO, DepositDTO, BailInsuranceDTO]])
def list_guarantees(
    skip: int = 0, 
    limit: int = 10, 
    guarantee_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return GuaranteeController(db).get_paginated_guarantees(skip=skip, limit=limit, guarantee_type=guarantee_type)

@guarantee_router.get("/{guarantee_key}", response_model=Union[GuarantorDTO, DepositDTO, BailInsuranceDTO])
def get_guarantee(guarantee_key: str, db: Session = Depends(get_db)):
    return GuaranteeController(db).get_guarantee(guarantee_key)

@guarantee_router.put("/{guarantee_key}", response_model=Union[GuarantorDTO, DepositDTO, BailInsuranceDTO])
def update_guarantee(guarantee_key: str, schema: GuaranteeSchema, db: Session = Depends(get_db)):
    return GuaranteeController(db).update_guarantee(guarantee_key, schema)

@guarantee_router.delete("/{guarantee_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_guarantee(guarantee_key: str, db: Session = Depends(get_db)):
    GuaranteeController(db).delete_guarantee(guarantee_key)