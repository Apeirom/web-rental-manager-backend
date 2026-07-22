from sqlalchemy.orm import Session
from typing import Union

from src.repository.guarantee_repository import GuaranteeRepository

from src.schemas.guarantee_schema import GuaranteeSchema,DepositSchema, GuarantorSchema, BailInsuranceSchema

from src.dto.guarantee_dto import DepositDTO, GuarantorDTO, BailInsuranceDTO

from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import (
    GuaranteeNotFoundError, 
    GuarantorDuplicateDocumentError,
    GuarantorNotFoundError,
    BailInsuranceNotFoundError,
    DepositNotFoundError
)

class GuaranteeController:
    def __init__(self, db: Session):
        self.guarantee_repository = GuaranteeRepository(db)

    def create_guarantee(self, schema: GuaranteeSchema) -> Union[GuarantorDTO, DepositDTO, BailInsuranceDTO]:
        if schema.type == "deposit":
            return self.create_deposit(schema)
        elif schema.type == "guarantor":
            return self.create_guarantor(schema)
        elif schema.type == "bail_insurance":
            return self.create_bail_insurance(schema)

    def create_guarantor(self, schema: GuarantorSchema) -> GuarantorDTO:
        existing = self.guarantee_repository.get_guarantor_by_document(schema.document_number)
        if existing:
            raise GuarantorDuplicateDocumentError(document_number=schema.document_number)

        model = self.guarantee_repository.create_guarantor(
            name=schema.name,
            document_number=schema.document_number
        )
        return GuarantorDTO.model_validate(model)

    def create_deposit(self, schema: DepositSchema) -> DepositDTO:
        model = self.guarantee_repository.create_deposit(
            amount=schema.amount,
            paid_in_cash=schema.paid_in_cash,
            deposit_date=schema.deposit_date
        )
        return DepositDTO.model_validate(model)

    def create_bail_insurance(self, schema: BailInsuranceSchema) -> BailInsuranceDTO:
        model = self.guarantee_repository.create_bail_insurance(
            value=schema.value,
            validity=schema.validity,
            insurance_company=schema.insurance_company
        )
        return BailInsuranceDTO.model_validate(model)


    def get_guarantee(self, guarantee_key: str) -> Union[GuarantorDTO, DepositDTO, BailInsuranceDTO]:
        model = self.guarantee_repository.get_by_key(guarantee_key)
        if not model:
            raise GuaranteeNotFoundError(guarantee_key=guarantee_key)
        
        if model.type == "guarantor":
            return GuarantorDTO.model_validate(model)
        elif model.type == "deposit":
            return DepositDTO.model_validate(model)
        elif model.type == "bail_insurance":
            return BailInsuranceDTO.model_validate(model)
        else:
            raise ValueError(f"Tipo de garantia desconhecido: {model.type}")

    def get_paginated_guarantees(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        guarantee_type: str = None
    ) -> PaginatedResponseDTO[Union[GuarantorDTO, DepositDTO, BailInsuranceDTO]]:
        
        total_count, models = self.guarantee_repository.get_paginated(
            skip=skip, 
            limit=limit, 
            guarantee_type=guarantee_type
        )
        
        dtos = []
        for m in models:
            if m.type == "guarantor":
                dtos.append(GuarantorDTO.model_validate(m))
            elif m.type == "deposit":
                dtos.append(DepositDTO.model_validate(m))
            elif m.type == "bail_insurance":
                dtos.append(BailInsuranceDTO.model_validate(m))
        
        return PaginatedResponseDTO(
            total=total_count,
            skip=skip,
            limit=limit,
            data=dtos
        )

    def update_guarantee(self, guarantee_key: str, schema: GuaranteeSchema) -> Union[GuarantorDTO, DepositDTO, BailInsuranceDTO]:
        if schema.type == "deposit":
            return self.update_deposit(guarantee_key, schema)
        elif schema.type == "guarantor":
            return self.update_guarantor(guarantee_key, schema)
        elif schema.type == "bail_insurance":
            return self.update_bail_insurance(guarantee_key, schema)

    def update_guarantor(self, guarantee_key: str, schema: GuarantorSchema) -> GuarantorDTO:
        model = self.guarantee_repository.get_by_key(guarantee_key)
        if not model or model.type != "guarantor":
            raise GuarantorNotFoundError(guarantor_key=guarantee_key)

        if model.document_number != schema.document_number:
            existing = self.guarantee_repository.get_guarantor_by_document(schema.document_number)
            if existing:
                raise GuarantorDuplicateDocumentError(document_number=schema.document_number)

        updated_model = self.guarantee_repository.update_guarantor(
            model=model,
            name=schema.name,
            document_number=schema.document_number
        )
        return GuarantorDTO.model_validate(updated_model)

    def update_deposit(self, guarantee_key: str, schema: DepositSchema) -> DepositDTO:
        model = self.guarantee_repository.get_by_key(guarantee_key)
        if not model or model.type != "deposit":
            raise DepositNotFoundError(deposit_key=guarantee_key)

        updated_model = self.guarantee_repository.update_deposit(
            model=model,
            amount=schema.amount,
            paid_in_cash=schema.paid_in_cash,
            deposit_date=schema.deposit_date
        )
        return DepositDTO.model_validate(updated_model)

    def update_bail_insurance(self, guarantee_key: str, schema: BailInsuranceSchema) -> BailInsuranceDTO:
        model = self.guarantee_repository.get_by_key(guarantee_key)
        if not model or model.type != "bail_insurance":
            raise BailInsuranceNotFoundError(bail_insurance_key=guarantee_key)

        updated_model = self.guarantee_repository.update_bail_insurance(
            model=model,
            value=schema.value,
            validity=schema.validity,
            insurance_company=schema.insurance_company
        )
        return BailInsuranceDTO.model_validate(updated_model)

    def delete_guarantee(self, guarantee_key: str) -> None:
        model = self.guarantee_repository.get_by_key(guarantee_key)
        if not model:
            raise GuaranteeNotFoundError(guarantee_key=guarantee_key)
            
        self.guarantee_repository.delete(model)