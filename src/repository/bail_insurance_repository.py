from sqlalchemy.orm import Session
from src.models import BailInsuranceModel, ContractModel, ContractStatusModel
from src.repository.base_repository import BaseRepository

class BailInsuranceRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, value: float, validity: str, insurance_company: str) -> BailInsuranceModel:
        bail_insurance = BailInsuranceModel(
            value=value,
            validity=validity,
            insurance_company=insurance_company
        )
        self.db.add(bail_insurance)
        self.db.flush()
        return bail_insurance

    def get_by_key(self, bail_insurance_key: str) -> BailInsuranceModel | None:
        return self.db.query(BailInsuranceModel).filter(BailInsuranceModel.key == bail_insurance_key).first()

    def get_paginated(
        self,
        skip: int = 0,
        limit: int = 10,
        search_term: str | None = None,
        insurance_company: str | None = None,
        validity: str | None = None,
        only_active_contracts: bool = False
    ) -> tuple[int, list[BailInsuranceModel]]:
        
        query = self.db.query(BailInsuranceModel)

        if search_term:
            query = query.filter(
                BailInsuranceModel.insurance_company.ilike(f"%{search_term}%")
            )

        if insurance_company:
            query = query.filter(BailInsuranceModel.insurance_company.ilike(f"%{insurance_company}%"))
            
        if validity:
            query = query.filter(BailInsuranceModel.validity.ilike(f"%{validity}%"))

        if only_active_contracts:
            query = query.join(ContractModel, ContractModel.bail_insurance_id == BailInsuranceModel.id) \
                         .join(ContractStatusModel, ContractModel.status_id == ContractStatusModel.id) \
                         .filter(ContractStatusModel.enumerator == "active") \
                         .distinct()

        total_count = query.count()
        items = query.offset(skip).limit(limit).all()

        return total_count, items

    def update(self, bail_insurance_model: BailInsuranceModel, value: float, validity: str, insurance_company: str) -> BailInsuranceModel:
        bail_insurance_model.value = value
        bail_insurance_model.validity = validity
        bail_insurance_model.insurance_company = insurance_company
        self.db.flush()
        return bail_insurance_model

    def delete(self, bail_insurance_model: BailInsuranceModel) -> None:
        self.db.delete(bail_insurance_model)