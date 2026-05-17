from sqlalchemy.orm import Session
from src.repository.payment_repository import PaymentRepository
from src.repository.contract_repository import ContractRepository
from src.schemas.payment_schema import PaymentCreateSchema, PaymentUpdateSchema
from src.dto.payment_dto import PaymentDTO
from src.errors.custom_errors import PaymentNotFoundError, PaymentInvalidRelationError

class PaymentController:
    def __init__(self, db: Session):
        self.repository = PaymentRepository(db)
        self.contract_repo = ContractRepository(db)

    def create_payment(self, schema: PaymentCreateSchema) -> PaymentDTO:
        contract_model = self.contract_repo.get_by_key(schema.contract_key)
        if not contract_model:
            raise PaymentInvalidRelationError(entity_name="Contract", key=schema.contract_key)

        payment_model = self.repository.create(
            payment_date=schema.payment_date,
            month_ref=schema.month_ref,
            year_ref=schema.year_ref,
            receipt_path=schema.receipt_path,
            contract_id=contract_model.id
        )
        return PaymentDTO.model_validate(payment_model)

    def get_payment(self, payment_key: str) -> PaymentDTO:
        payment_model = self.repository.get_by_key(payment_key)
        if not payment_model:
            raise PaymentNotFoundError(payment_key=payment_key)
        return PaymentDTO.model_validate(payment_model)

    def get_all_payments(self) -> list[PaymentDTO]:
        entities = self.repository.get_all()
        return [PaymentDTO.model_validate(e) for e in entities]

    def update_payment(self, payment_key: str, schema: PaymentUpdateSchema) -> PaymentDTO:
        payment_model = self.repository.get_by_key(payment_key)
        if not payment_model:
            raise PaymentNotFoundError(payment_key=payment_key)

        contract_model = self.contract_repo.get_by_key(schema.contract_key)
        if not contract_model:
            raise PaymentInvalidRelationError(entity_name="Contract", key=schema.contract_key)

        updated_model = self.repository.update(
            payment_model=payment_model,
            payment_date=schema.payment_date,
            month_ref=schema.month_ref,
            year_ref=schema.year_ref,
            receipt_path=schema.receipt_path,
            contract_id=contract_model.id
        )
        return PaymentDTO.model_validate(updated_model)

    def delete_payment(self, payment_key: str) -> None:
        payment_model = self.repository.get_by_key(payment_key)
        if not payment_model:
            raise PaymentNotFoundError(payment_key=payment_key)
        self.repository.delete(payment_model)