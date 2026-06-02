from sqlalchemy.orm import Session
from src.repository.tenant_repository import TenantRepository
from src.schemas.tenant_schema import TenantCreateSchema, TenantUpdateSchema
from src.dto.tenant_dto import TenantDTO
from src.errors.custom_errors import TenantNotFoundError, TenantDuplicateDocumentError
from src.dto.paginated_response import PaginatedResponseDTO

class TenantController:
    def __init__(self, db: Session):
        self.tenant_repository = TenantRepository(db)

    def create_tenant(self, schema: TenantCreateSchema) -> TenantDTO:
        existing_tenant = self.tenant_repository.get_by_document(schema.document_number)
        if existing_tenant:
            raise TenantDuplicateDocumentError(document_number=schema.document_number)
            
        tenant_model = self.tenant_repository.create(
            name=schema.name,
            document_number=schema.document_number
        )
        return TenantDTO.model_validate(tenant_model)

    def get_tenant(self, tenant_key: str) -> TenantDTO:
        tenant_model = self.tenant_repository.get_by_key(tenant_key)
        if not tenant_model:
            raise TenantNotFoundError(tenant_key=tenant_key)
        return TenantDTO.model_validate(tenant_model)

    def get_paginated_tenants(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search_term: str = None,
        name: str = None,
        document_number: str = None,
        only_active_contracts: bool = False
    ) -> PaginatedResponseDTO[TenantDTO]:
        
        total_count, tenant_models = self.tenant_repository.get_paginated(
            skip=skip, 
            limit=limit, 
            search_term=search_term,
            name=name,
            document_number=document_number,
            only_active_contracts=only_active_contracts
        )
        
        tenant_dtos = [TenantDTO.model_validate(t) for t in tenant_models]
        
        return PaginatedResponseDTO(
            total=total_count,
            skip=skip,
            limit=limit,
            data=tenant_dtos
        )

    def update_tenant(self, tenant_key: str, schema: TenantUpdateSchema) -> TenantDTO:
        tenant_model = self.tenant_repository.get_by_key(tenant_key)
        if not tenant_model:
            raise TenantNotFoundError(tenant_key=tenant_key)
            
        if tenant_model.document_number != schema.document_number:
            existing = self.tenant_repository.get_by_document(schema.document_number)
            if existing:
                raise TenantDuplicateDocumentError(document_number=schema.document_number)

        updated_model = self.tenant_repository.update(
            tenant_model=tenant_model,
            name=schema.name,
            document_number=schema.document_number
        )
        return TenantDTO.model_validate(updated_model)

    def delete_tenant(self, tenant_key: str) -> None:
        tenant_model = self.tenant_repository.get_by_key(tenant_key)
        if not tenant_model:
            raise TenantNotFoundError(tenant_key=tenant_key)
        self.tenant_repository.delete(tenant_model)