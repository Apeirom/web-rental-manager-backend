from sqlalchemy.orm import Session
from sqlalchemy import or_, update
from src.repository.base_repository import BaseRepository
from src.models import (
    ContractModel,
    ContractStatusModel,
    PropertyModel,
    TenantModel,
    RealEstateModel,
    GuaranteeModel
)
from src.repository.contract_status_event_repository import (
    ContractStatusEventRepository,
)
from src.repository.extract_repository import ExtractRepository

class ContractRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(
        self, 
        rent_amount: float, 
        room_name: str | None, 
        status: ContractStatusModel, 
        file_path: str | None, 
        property: PropertyModel, 
        tenant: TenantModel, 
        real_estate: RealEstateModel | None, 
        guarantee: GuaranteeModel | None
    ) -> ContractModel:
        contract = ContractModel(
            rent_amount=rent_amount,
            room_name=room_name,
            status=status,
            file_path=file_path,
            property=property,
            tenant=tenant,
            real_estate=real_estate,
            guarantee=guarantee
        )
        self.db.add(contract)
        self.db.flush()
        return contract

    def get_by_key(self, contract_key: str) -> ContractModel | None:
        return self.db.query(ContractModel).filter(ContractModel.key == contract_key).first()

    def get_by_property_id(self, property_id: int) -> list[ContractModel]:
        return (
            self.db.query(ContractModel)
            .filter(ContractModel.property_id == property_id)
            .all()
        )

    def get_by_property_ids(self, property_ids: set[int]) -> list[ContractModel]:
        if not property_ids:
            return []
        return (
            self.db.query(ContractModel)
            .filter(ContractModel.property_id.in_(property_ids))
            .all()
        )

    def get_by_tenant_id(self, tenant_id: int) -> list[ContractModel]:
        return (
            self.db.query(ContractModel)
            .filter(ContractModel.tenant_id == tenant_id)
            .all()
        )

    def get_by_guarantee_id(self, guarantee_id: int) -> list[ContractModel]:
        return (
            self.db.query(ContractModel)
            .filter(ContractModel.guarantee_id == guarantee_id)
            .all()
        )

    def count_by_guarantee_id(self, guarantee_id: int) -> int:
        return (
            self.db.query(ContractModel)
            .filter(ContractModel.guarantee_id == guarantee_id)
            .count()
        )

    def clear_real_estate_reference(self, real_estate_id: int) -> None:
        self.db.execute(
            update(ContractModel)
            .where(ContractModel.real_estate_id == real_estate_id)
            .values(real_estate_id=None)
        )
        self.db.flush()

    def update_file_path(
        self,
        contract_model: ContractModel,
        file_path: str,
    ) -> ContractModel:
        contract_model.file_path = file_path
        self.db.flush()
        return contract_model

    def update(
        self, 
        contract_model: ContractModel, 
        rent_amount: float, 
        room_name: str | None, 
        status: ContractStatusModel, 
        file_path: str | None, 
        property: PropertyModel, 
        tenant: TenantModel, 
        real_estate: RealEstateModel | None, 
        guarantee: GuaranteeModel | None
    ) -> ContractModel:
        contract_model.rent_amount = rent_amount
        contract_model.room_name = room_name
        contract_model.status = status
        contract_model.file_path = file_path
        contract_model.property = property
        contract_model.tenant = tenant
        contract_model.real_estate = real_estate
        contract_model.guarantee = guarantee
        self.db.flush()
        return contract_model

    def delete(self, contract_model: ContractModel) -> None:
        self.delete_many([contract_model])

    def delete_many(self, contracts: list[ContractModel]) -> None:
        if not contracts:
            return

        extract_repository = ExtractRepository(self.db)
        contract_status_event_repository = ContractStatusEventRepository(self.db)
        contract_ids = {contract.id for contract in contracts}
        extracts = extract_repository.get_by_contract_ids(contract_ids)
        extract_repository.delete_many(extracts)
        contract_status_event_repository.delete_by_contract_ids(contract_ids)

        for contract in contracts:
            self.db.delete(contract)
        self.db.flush()

    def get_paginated(
        self,
        skip: int = 0,
        limit: int = 10,
        search_term: str | None = None,
        room_name: str | None = None,
        property_name: str | None = None,
        tenant_name: str | None = None,
        real_estate_name: str | None = None,
        status: str | None = None
    ) -> tuple[int, list[ContractModel]]:
        
        query = self.db.query(ContractModel)

        if search_term:
            query = query.join(ContractModel.property).join(ContractModel.tenant).filter(
                or_(
                    PropertyModel.property_name.ilike(f"%{search_term}%"),
                    TenantModel.name.ilike(f"%{search_term}%")
                )
            )
            query = query.reset_joinpoint()

        if room_name:
            query = query.filter(ContractModel.room_name.ilike(f"%{room_name}%"))
        
        if property_name:
            query = query.join(ContractModel.property).filter(PropertyModel.property_name.ilike(f"%{property_name}%"))
            query = query.reset_joinpoint()
            
        if tenant_name:
            query = query.join(ContractModel.tenant).filter(TenantModel.name.ilike(f"%{tenant_name}%"))
            query = query.reset_joinpoint()
            
        if real_estate_name:
            query = query.join(ContractModel.real_estate).filter(RealEstateModel.name.ilike(f"%{real_estate_name}%"))
            query = query.reset_joinpoint()

        if status:
            query = query.join(ContractModel.status).filter(ContractStatusModel.enumerator == status)
            query = query.reset_joinpoint()

        total_count = query.count()
        items = query.offset(skip).limit(limit).all()

        return total_count, items