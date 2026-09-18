from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from src.database.config import get_db
from typing import Optional

from src.utils.security import get_user_info_by_token

from src.dto.paginated_response import PaginatedResponseDTO
from src.dto.contract_dto import ContractDTO
from src.schemas.contract_schema import ContractSchema
from src.controller.contract_controller import ContractController

bearer_scheme = HTTPBearer()

contract_router = APIRouter(
    prefix="/contracts",
    tags=["7. Contratos (Contracts)"],
    dependencies=[Depends(bearer_scheme)]
)

@contract_router.post("", response_model=ContractDTO, status_code=status.HTTP_201_CREATED)
def create_contract(
    schema: ContractSchema, 
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(get_user_info_by_token)
):
    return ContractController(db).create_contract(schema, current_user_data)

@contract_router.get("/{contract_key}", response_model=ContractDTO)
def get_contract(contract_key: str, db: Session = Depends(get_db)):
    return ContractController(db).get_contract(contract_key)

@contract_router.put("/{contract_key}", response_model=ContractDTO)
def update_contract(
    contract_key: str, 
    schema: ContractSchema, 
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(get_user_info_by_token)
):
    return ContractController(db).update_contract(contract_key, schema, current_user_data)

@contract_router.delete("/{contract_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(contract_key: str, db: Session = Depends(get_db)):
    ContractController(db).delete_contract(contract_key)

@contract_router.post("/{contract_key}/upload-document", response_model=ContractDTO)
def upload_contract_document(
    contract_key: str, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    file_bytes = file.file.read()
    return ContractController(db).upload_document(
        contract_key=contract_key, 
        file_bytes=file_bytes, 
        content_type=file.content_type
    )

@contract_router.get("", response_model=PaginatedResponseDTO[ContractDTO])
def list_contracts(
    skip: int = 0, 
    limit: int = 10,
    search_term: Optional[str] = None,
    room_name: Optional[str] = None,
    property_name: Optional[str] = None,
    tenant_name: Optional[str] = None,
    real_estate_name: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return ContractController(db).get_paginated_contracts(
        skip, limit, search_term, room_name, property_name, tenant_name, real_estate_name, status
    )