from sqlalchemy.orm import Session
from src.models import PaymentModel, PaymentStatusModel, ExtractModel
from src.repository.base_repository import BaseRepository

class PaymentRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, payment_date: str, amount: float, status: PaymentStatusModel) -> PaymentModel:
        payment = PaymentModel(
            payment_date=payment_date,
            amount=amount,
            status=status
        )
        self.db.add(payment)
        self.db.flush()
        return payment
    
    def get_by_key(self, key: str) -> PaymentModel | None:
        return self.db.query(PaymentModel).filter(PaymentModel.key == key).first()
    
    def update(
        self, 
        payment_model: PaymentModel, 
        payment_date: str | None = None, 
        amount: float | None = None, 
        status: PaymentStatusModel | None = None,
        extract: ExtractModel | None = None
    ) -> PaymentModel:
        
        if payment_date is not None:
            payment_model.payment_date = payment_date
        
        if amount is not None:
            payment_model.amount = amount
            
        if status is not None:
            payment_model.status = status
            
        if extract is not None:
            payment_model.extract = extract

        self.db.flush()
        return payment_model
    
    def delete(self, payment_model: PaymentModel) -> None:
        self.db.delete(payment_model)
        self.db.flush()

    def get_paginated(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        amount: float | None = None,
        payment_date: str | None = None,
        status_enumerator: str | None = None
    ) -> tuple[int, list[PaymentModel]]:
        query = self.db.query(PaymentModel)

        if amount is not None:
            query = query.filter(PaymentModel.amount == amount)
        
        if payment_date:
            query = query.filter(PaymentModel.payment_date.startswith(payment_date))

        if status_enumerator:
            query = query.join(PaymentStatusModel).filter(
                PaymentStatusModel.enumerator == status_enumerator
            )

        query = query.order_by(PaymentModel.payment_date.desc())

        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return total, items

    