from sqlalchemy.orm import Session
from src.repository.payment_repository import PaymentRepository
from src.repository.contract_repository import ContractRepository
from src.schemas.payment_schema import PaymentCreateSchema, PaymentUpdateSchema
from src.dto.payment_dto import PaymentDTO
from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import PaymentNotFoundError, PaymentInvalidRelationError

class PaymentController:
    def __init__(self, db: Session):
        self.payment_repository = PaymentRepository(db)
        self.contract_repo = ContractRepository(db)

    def create_payment(self, schema: PaymentCreateSchema) -> PaymentDTO:
        contract_model = self.contract_repo.get_by_key(schema.contract_key)
        if not contract_model:
            raise PaymentInvalidRelationError(entity_name="Contract", key=schema.contract_key)

        payment_model = self.payment_repository.create(
            payment_date=schema.payment_date,
            month_ref=schema.month_ref,
            year_ref=schema.year_ref,
            file_path=schema.file_path,
            contract_id=contract_model.id
        )
        return PaymentDTO.model_validate(payment_model)

    def get_payment(self, payment_key: str) -> PaymentDTO:
        payment_model = self.payment_repository.get_by_key(payment_key)
        if not payment_model:
            raise PaymentNotFoundError(payment_key=payment_key)
        return PaymentDTO.model_validate(payment_model)

    def get_paginated_payments(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search_term: str = None,
        only_active_contracts: bool = False
    ) -> PaginatedResponseDTO[PaymentDTO]:
        
        total_count, payment_models = self.payment_repository.get_paginated(
            skip=skip, 
            limit=limit, 
            search_term=search_term,
            only_active_contracts=only_active_contracts
        )
        
        payment_dtos = [PaymentDTO.model_validate(p) for p in payment_models]
        
        return PaginatedResponseDTO(
            total=total_count,
            skip=skip,
            limit=limit,
            data=payment_dtos
        )

    def update_payment(self, payment_key: str, schema: PaymentUpdateSchema) -> PaymentDTO:
        payment_model = self.payment_repository.get_by_key(payment_key)
        if not payment_model:
            raise PaymentNotFoundError(payment_key=payment_key)

        contract_model = self.contract_repo.get_by_key(schema.contract_key)
        if not contract_model:
            raise PaymentInvalidRelationError(entity_name="Contract", key=schema.contract_key)

        updated_model = self.payment_repository.update(
            payment_model=payment_model,
            payment_date=schema.payment_date,
            month_ref=schema.month_ref,
            year_ref=schema.year_ref,
            file_path=schema.file_path,
            contract_id=contract_model.id
        )
        return PaymentDTO.model_validate(updated_model)

    def delete_payment(self, payment_key: str) -> None:
        payment_model = self.payment_repository.get_by_key(payment_key)
        if not payment_model:
            raise PaymentNotFoundError(payment_key=payment_key)
        self.payment_repository.delete(payment_model)