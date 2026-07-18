from sqlalchemy.orm import Session
from src.repository.payment_repository import PaymentRepository
from src.repository.extract_batch_repository import ExtractBatchRepository
from src.schemas.payment_schema import PaymentCreateSchema, PaymentUpdateSchema
from src.dto.payment_dto import PaymentDTO
from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import PaymentNotFoundError, ExtractNotFoundError

class PaymentController:
    def __init__(self, db: Session):
        self.payment_repository = PaymentRepository(db)
        self.extract_batch_repository = ExtractBatchRepository(db)

    def create_payment(self, schema: PaymentCreateSchema) -> PaymentDTO:
        payment_model = self.payment_repository.create(
            payment_date=schema.payment_date,
            amount=schema.amount,
        )
        return PaymentDTO.model_validate(payment_model)

    def get_payment(self, payment_key: str) -> PaymentDTO:
        payment_model = self.payment_repository.get_by_key(payment_key)
        if not payment_model:
            raise PaymentNotFoundError(payment_key=payment_key)
        return PaymentDTO.model_validate(payment_model)

    def update_payment(self, payment_key: str, schema: PaymentUpdateSchema) -> PaymentDTO:
        payment_model = self.payment_repository.get_by_key(payment_key)
        if not payment_model:
            raise PaymentNotFoundError(payment_key=payment_key)

        extract_batch_model = None
        if schema.extract_batch_key:
            extract_batch_model = self.extract_batch_repository.get_by_key(schema.extract_batch_key)
            if not extract_batch_model:
                raise ExtractNotFoundError(schema.extract_batch_key)
        
        updated_model = self.payment_repository.update(
            payment_model=payment_model,
            payment_date=schema.payment_date,
            amount=schema.amount,
            extract_batch=extract_batch_model
        )
        
        return PaymentDTO.model_validate(updated_model)
    
    def get_paginated_payments(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        amount: float | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        is_linked: bool | None = None
    ) -> PaginatedResponseDTO[PaymentDTO]:
        
        total_count, payment_models = self.payment_repository.get_paginated(
            skip=skip, 
            limit=limit, 
            amount=amount,
            start_date=start_date,
            end_date=end_date,
            is_linked=is_linked
        )
        
        payment_dtos = [PaymentDTO.model_validate(p) for p in payment_models]
        
        return PaginatedResponseDTO(
            total=total_count,
            skip=skip,
            limit=limit,
            data=payment_dtos
        )
    
    def delete_payment(self, payment_key: str) -> None:
        payment_model = self.payment_repository.get_by_key(payment_key)
        if not payment_model:
            raise PaymentNotFoundError(payment_key=payment_key)
        
        self.payment_repository.delete(payment_model)