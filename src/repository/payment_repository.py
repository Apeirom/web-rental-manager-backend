from sqlalchemy.orm import Session
from src.models.payment_model import PaymentModel
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

    def get_all(self) -> list[PaymentModel]:
        return self.db.query(PaymentModel).all()

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