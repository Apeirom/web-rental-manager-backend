from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.models import PaymentModel, ContractModel, PropertyModel, TenantModel, ContractStatusModel
from src.repository.base_repository import BaseRepository 


class PaymentRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, payment_date: str, month_ref: int, year_ref: int, file_path: str | None, contract_id: int) -> PaymentModel:
        payment = PaymentModel(
            payment_date=payment_date,
            month_ref=month_ref,
            year_ref=year_ref,
            file_path=file_path,
            contract_id=contract_id
        )
        self.db.add(payment)
        self.db.flush()
        return payment

    def get_by_key(self, payment_key: str) -> PaymentModel | None:
        return self.db.query(PaymentModel).filter(PaymentModel.key == payment_key).first()

    def get_paginated(
        self,
        skip: int = 0,
        limit: int = 10,
        search_term: str | None = None,
        only_active_contracts: bool = False
    ) -> tuple[int, list[PaymentModel]]:
        
        query = self.db.query(PaymentModel)

        if search_term:
            query = query.join(PaymentModel.contract).join(ContractModel.property).join(ContractModel.tenant).filter(
                or_(
                    PropertyModel.property_name.ilike(f"%{search_term}%"),
                    TenantModel.name.ilike(f"%{search_term}%")
                )
            )
            query = query.reset_joinpoint()

        if only_active_contracts:
            query = query.join(PaymentModel.contract).join(ContractStatusModel, ContractModel.status_id == ContractStatusModel.id).filter(
                ContractStatusModel.enumerator == "active"
            )
            query = query.reset_joinpoint()

        total_count = query.count()
        items = query.offset(skip).limit(limit).all()

        return total_count, items

    def update(self, payment_model: PaymentModel, payment_date: str, month_ref: int, year_ref: int, file_path: str | None, contract_id: int) -> PaymentModel:
        payment_model.payment_date = payment_date
        payment_model.month_ref = month_ref
        payment_model.year_ref = year_ref
        payment_model.file_path = file_path
        payment_model.contract_id = contract_id
        self.db.flush()
        return payment_model

    def delete(self, payment_model: PaymentModel) -> None:
        self.db.delete(payment_model)
        self.db.flush()