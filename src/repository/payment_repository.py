from sqlalchemy.orm import Session
from src.models import PaymentModel, ExtractBatchModel
from src.repository.base_repository import BaseRepository

class PaymentRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, payment_date: str, amount: float) -> PaymentModel:
        payment = PaymentModel(
            payment_date=payment_date,
            amount=amount,
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
        extract_batch: ExtractBatchModel | None = None
    ) -> PaymentModel:
        
        payment_model.payment_date = payment_date
        payment_model.amount = amount    
        payment_model.extract_batch = extract_batch

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
        start_date: str | None = None,
        end_date: str | None = None,
        is_linked: bool | None = None
    ) -> tuple[int, list[PaymentModel]]:
        query = self.db.query(PaymentModel)

        if amount is not None:
            query = query.filter(PaymentModel.amount == amount)
        
        if start_date:
            query = query.filter(PaymentModel.payment_date >= start_date)

        if end_date:
            query = query.filter(PaymentModel.payment_date <= end_date)

        if is_linked is True:
            query = query.filter(PaymentModel.extract_batch.has())
        elif is_linked is False:
            query = query.filter(~PaymentModel.extract_batch.has())

        query = query.order_by(PaymentModel.payment_date.desc())

        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return total, items

    