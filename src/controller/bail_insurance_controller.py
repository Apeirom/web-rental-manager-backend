from sqlalchemy.orm import Session
from src.repository.bail_insurance_repository import BailInsuranceRepository
from src.schemas.bail_insurance_schema import BailInsuranceCreateSchema, BailInsuranceUpdateSchema
from src.dto.bail_insurance_dto import BailInsuranceDTO
from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import BailInsuranceNotFoundError

class BailInsuranceController:
    def __init__(self, db: Session):
        self.bail_insurance_repository = BailInsuranceRepository(db)

    def create_bail_insurance(self, schema: BailInsuranceCreateSchema) -> BailInsuranceDTO:
        bail_insurance_model = self.bail_insurance_repository.create(
            value=schema.value,
            validity=schema.validity,
            insurance_company=schema.insurance_company
        )
        return BailInsuranceDTO.model_validate(bail_insurance_model)

    def get_bail_insurance(self, bail_insurance_key: str) -> BailInsuranceDTO:
        bail_insurance_model = self.bail_insurance_repository.get_by_key(bail_insurance_key)
        if not bail_insurance_model:
            raise BailInsuranceNotFoundError(bail_insurance_key=bail_insurance_key)
        return BailInsuranceDTO.model_validate(bail_insurance_model)

    def get_paginated_bail_insurances(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search_term: str = None,
        insurance_company: str = None,
        validity: str = None,
        only_active_contracts: bool = False
    ) -> PaginatedResponseDTO[BailInsuranceDTO]:
        
        total_count, bail_insurance_models = self.bail_insurance_repository.get_paginated(
            skip=skip, 
            limit=limit, 
            search_term=search_term,
            insurance_company=insurance_company,
            validity=validity,
            only_active_contracts=only_active_contracts
        )
        
        bail_insurance_dtos = [BailInsuranceDTO.model_validate(e) for e in bail_insurance_models]
        
        return PaginatedResponseDTO(
            total=total_count,
            skip=skip,
            limit=limit,
            data=bail_insurance_dtos
        )

    def update_bail_insurance(self, bail_insurance_key: str, schema: BailInsuranceUpdateSchema) -> BailInsuranceDTO:
        bail_insurance_model = self.bail_insurance_repository.get_by_key(bail_insurance_key)
        if not bail_insurance_model:
            raise BailInsuranceNotFoundError(bail_insurance_key=bail_insurance_key)

        updated_model = self.bail_insurance_repository.update(
            bail_insurance_model=bail_insurance_model,
            value=schema.value,
            validity=schema.validity,
            insurance_company=schema.insurance_company
        )
        return BailInsuranceDTO.model_validate(updated_model)

    def delete_bail_insurance(self, bail_insurance_key: str) -> None:
        bail_insurance_model = self.bail_insurance_repository.get_by_key(bail_insurance_key)
        if not bail_insurance_model:
            raise BailInsuranceNotFoundError(bail_insurance_key=bail_insurance_key)
        self.bail_insurance_repository.delete(bail_insurance_model)