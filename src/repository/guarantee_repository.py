from sqlalchemy.orm import Session
from src.repository.base_repository import BaseRepository
from src.models import (
    GuaranteeModel, 
    DepositModel, 
    GuarantorModel, 
    BailInsuranceModel
)

class GuaranteeRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)


    def create_deposit(self, amount: float, paid_in_cash: bool = False, deposit_date: str = None) -> DepositModel:
        deposit = DepositModel(amount=amount, paid_in_cash=paid_in_cash, deposit_date=deposit_date)
        self.db.add(deposit)
        self.db.flush()
        return deposit

    def create_guarantor(self, name: str, document_number: str) -> GuarantorModel:
        guarantor = GuarantorModel(name=name, document_number=document_number)
        self.db.add(guarantor)
        self.db.flush()
        return guarantor

    def create_bail_insurance(self, value: float, validity: str, insurance_company: str) -> BailInsuranceModel:
        bail_insurance = BailInsuranceModel(
            value=value, 
            validity=validity, 
            insurance_company=insurance_company
        )
        self.db.add(bail_insurance)
        self.db.flush()
        return bail_insurance


    def get_by_key(self, key: str) -> GuaranteeModel:
        return self.db.query(GuaranteeModel).filter(GuaranteeModel.key == key).first()

    def get_guarantor_by_document(self, document_number: str) -> GuarantorModel:
        return self.db.query(GuarantorModel).filter(GuarantorModel.document_number == document_number).first()

    def get_paginated(
        self,
        skip: int = 0,
        limit: int = 10,
        guarantee_type: str | None = None
    ) -> tuple[int, list[GuaranteeModel]]:
        
        query = self.db.query(GuaranteeModel)

        if guarantee_type:
            query = query.filter(GuaranteeModel.type == guarantee_type)

        total_count = query.count()
        items = query.offset(skip).limit(limit).all()

        return total_count, items


    def update_deposit(self, model: DepositModel, amount: float, paid_in_cash: bool, deposit_date: str) -> DepositModel:
        model.amount = amount
        model.paid_in_cash = paid_in_cash
        model.deposit_date = deposit_date
        self.db.flush()
        return model

    def update_guarantor(self, model: GuarantorModel, name: str, document_number: str) -> GuarantorModel:
        model.name = name
        model.document_number = document_number
        self.db.flush()
        return model

    def update_bail_insurance(self, model: BailInsuranceModel, value: float, validity: str, insurance_company: str) -> BailInsuranceModel:
        model.value = value
        model.validity = validity
        model.insurance_company = insurance_company
        self.db.flush()
        return model
    

    def delete(self, model: GuaranteeModel) -> None:
        self.db.delete(model)
        self.db.flush()