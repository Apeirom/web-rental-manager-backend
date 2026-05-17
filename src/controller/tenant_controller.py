from sqlalchemy.orm import Session
from src.repository.tenant_repository import TenantRepository
from src.schemas.tenant_schema import TenantCreateSchema, TenantUpdateSchema
from src.dto.tenant_dto import TenantDTO
from src.errors.custom_errors import TenantNotFoundError, TenantDuplicateDocumentError

class TenantController:
    def __init__(self, db: Session):
        self.repository = TenantRepository(db)

    def create_tenant(self, schema: TenantCreateSchema) -> TenantDTO:
        existing_tenant = self.repository.get_by_document(schema.document_number)
        if existing_tenant:
            raise TenantDuplicateDocumentError(document_number=schema.document_number)
            
        tenant_model = self.repository.create(
            name=schema.name,
            document_number=schema.document_number
        )
        return TenantDTO.model_validate(tenant_model)

    def get_tenant(self, tenant_key: str) -> TenantDTO:
        tenant_model = self.repository.get_by_key(tenant_key)
        if not tenant_model:
            raise TenantNotFoundError(tenant_key=tenant_key)
        return TenantDTO.model_validate(tenant_model)

    def get_all_tenants(self) -> list[TenantDTO]:
        tenants = self.repository.get_all()
        return [TenantDTO.model_validate(t) for t in tenants]

    def update_tenant(self, tenant_key: str, schema: TenantUpdateSchema) -> TenantDTO:
        tenant_model = self.repository.get_by_key(tenant_key)
        if not tenant_model:
            raise TenantNotFoundError(tenant_key=tenant_key)
            
        if tenant_model.document_number != schema.document_number:
            existing = self.repository.get_by_document(schema.document_number)
            if existing:
                raise TenantDuplicateDocumentError(document_number=schema.document_number)

        updated_model = self.repository.update(
            tenant_model=tenant_model,
            name=schema.name,
            document_number=schema.document_number
        )
        return TenantDTO.model_validate(updated_model)

    def delete_tenant(self, tenant_key: str) -> None:
        tenant_model = self.repository.get_by_key(tenant_key)
        if not tenant_model:
            raise TenantNotFoundError(tenant_key=tenant_key)
        self.repository.delete(tenant_model)