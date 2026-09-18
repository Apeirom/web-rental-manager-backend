from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from src.database.config import get_db
from typing import Optional

from src.dto.paginated_response import PaginatedResponseDTO
from src.dto.tenant_dto import TenantDTO
from src.schemas.tenant_schema import TenantCreateSchema, TenantUpdateSchema
from src.controller.tenant_controller import TenantController

bearer_scheme = HTTPBearer()

tenant_router = APIRouter(
    prefix="/tenants",
    tags=["3. Inquilinos (Tenants)"],
    dependencies=[Depends(bearer_scheme)]
)

@tenant_router.post("", response_model=TenantDTO, status_code=status.HTTP_201_CREATED)
def create_tenant(schema: TenantCreateSchema, db: Session = Depends(get_db)):
    controller = TenantController(db)
    return controller.create_tenant(schema)

@tenant_router.get("", response_model=PaginatedResponseDTO[TenantDTO])
def list_tenants(
    skip: int = 0, 
    limit: int = 10, 
    search_term: Optional[str] = None,
    name: Optional[str] = None,
    document_number: Optional[str] = None,
    only_active_contracts: bool = False,
    db: Session = Depends(get_db)
):
    controller = TenantController(db)
    return controller.get_paginated_tenants(skip, limit, search_term, name, document_number, only_active_contracts)

@tenant_router.get("/{tenant_key}", response_model=TenantDTO)
def get_tenant(tenant_key: str, db: Session = Depends(get_db)):
    controller = TenantController(db)
    return controller.get_tenant(tenant_key)


@tenant_router.put("/{tenant_key}", response_model=TenantDTO)
def update_tenant(tenant_key: str, schema: TenantUpdateSchema, db: Session = Depends(get_db)):
    controller = TenantController(db)
    return controller.update_tenant(tenant_key, schema)

@tenant_router.delete("/{tenant_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(tenant_key: str, db: Session = Depends(get_db)):
    controller = TenantController(db)
    controller.delete_tenant(tenant_key)