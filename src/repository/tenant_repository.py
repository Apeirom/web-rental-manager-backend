from sqlalchemy.orm import Session
from src.models.tenant_model import TenantModel
from src.repository.base_repository import BaseRepository 


class TenantRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, name: str, document_number: str) -> TenantModel:
        tenant = TenantModel(name=name, document_number=document_number)
        self.db.add(tenant)
        self.db.flush()
        return tenant

    def get_by_key(self, tenant_key: str) -> TenantModel | None:
        return self.db.query(TenantModel).filter(TenantModel.key == tenant_key).first()

    def get_by_document(self, document_number: str) -> TenantModel | None:
        return self.db.query(TenantModel).filter(TenantModel.document_number == document_number).first()

    def get_all(self) -> list[TenantModel]:
        return self.db.query(TenantModel).all()

    def update(self, tenant_model: TenantModel, name: str, document_number: str) -> TenantModel:
        tenant_model.name = name
        tenant_model.document_number = document_number
        self.db.flush()
        return tenant_model

    def delete(self, tenant_model: TenantModel) -> None:
        self.db.delete(tenant_model)
        self.db.flush()