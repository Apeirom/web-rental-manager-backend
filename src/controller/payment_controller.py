from sqlalchemy.orm import Session
from src.repository.payment_repository import PaymentRepository
from src.repository.extract_repository import ExtractRepository
from src.schemas.payment_schema import PaymentCreateSchema, PaymentUpdateSchema
from src.dto.payment_dto import PaymentDTO
from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import PaymentNotFoundError, ExtractNotFoundError
from src.models import PaymentStatusModel

class PaymentController:
    def __init__(self, db: Session):
        self.payment_repository = PaymentRepository(db)
        self.extract_repository = ExtractRepository(db)

    def create_payment(self, schema: PaymentCreateSchema) -> PaymentDTO:
        status = self.payment_repository.get_enumerator_model(PaymentStatusModel,"unlinked")
        payment_model = self.payment_repository.create(
            payment_date=schema.payment_date,
            amount=schema.amount,
            status=status
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

        new_status = None
        if schema.status_enumerator:
            new_status = self.payment_repository.get_enumerator_model(PaymentStatusModel,schema.status_enumerator)

        extract_model = None
        if schema.extract_key:
            extract_model = self.extract_repository.get_by_key(schema.extract_key)
            if not extract_model:
                raise ExtractNotFoundError(schema.extract_key)
        
        updated_model = self.payment_repository.update(
            payment_model=payment_model,
            payment_date=schema.payment_date,
            amount=schema.amount,
            status=new_status,
            extract=extract_model
        )
        
        return PaymentDTO.model_validate(updated_model)
    
    def get_paginated_payments(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        amount: float | None = None,
        payment_date: str | None = None,
        status: str | None = None
    ) -> PaginatedResponseDTO[PaymentDTO]:
        
        total_count, payment_models = self.payment_repository.get_paginated(
            skip=skip, 
            limit=limit, 
            amount=amount,
            payment_date=payment_date,
            status_enumerator=status
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