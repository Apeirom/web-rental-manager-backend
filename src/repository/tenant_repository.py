from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.repository.base_repository import BaseRepository
from src.models import TenantModel, ContractModel, ContractStatusModel


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

    def get_paginated(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search_term: str | None = None,
        name: str | None = None,
        document_number: str | None = None,
        only_active_contracts: bool = False
    ) -> tuple[int, list[TenantModel]]:
        
        query = self.db.query(TenantModel)

        if search_term:
            query = query.filter(
                or_(
                    TenantModel.name.ilike(f"%{search_term}%"),
                    TenantModel.document_number.ilike(f"%{search_term}%")
                )
            )

        if name:
            query = query.filter(TenantModel.name.ilike(f"%{name}%"))
        if document_number:
            query = query.filter(TenantModel.document_number.ilike(f"%{document_number}%"))

        
        if only_active_contracts:
            query = query.join(ContractModel, ContractModel.tenant_id == TenantModel.id) \
                         .join(ContractStatusModel, ContractModel.status_id == ContractStatusModel.id) \
                         .filter(ContractStatusModel.enumerator == "active") \
                         .distinct()

        total_count = query.count()
        items = query.offset(skip).limit(limit).all()

        return total_count, items

    def update(self, tenant_model: TenantModel, name: str, document_number: str) -> TenantModel:
        tenant_model.name = name
        tenant_model.document_number = document_number
        self.db.flush()
        return tenant_model

    def delete(self, tenant_model: TenantModel) -> None:
        self.db.delete(tenant_model)
        self.db.flush()