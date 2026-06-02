from sqlalchemy.orm import Session
from src.repository.real_estate_repository import RealEstateRepository
from src.schemas.real_estate_schema import RealEstateCreateSchema, RealEstateUpdateSchema
from src.dto.real_estate_dto import RealEstateDTO
from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import RealEstateNotFoundError, RealEstateDuplicateCnpjError

class RealEstateController:
    def __init__(self, db: Session):
        self.real_estate_repository = RealEstateRepository(db)

    def create_real_estate(self, schema: RealEstateCreateSchema) -> RealEstateDTO:
        existing = self.real_estate_repository.get_by_cnpj(schema.cnpj)
        if existing:
            raise RealEstateDuplicateCnpjError(cnpj=schema.cnpj)

        real_estate_model = self.real_estate_repository.create(
            name=schema.name,
            cnpj=schema.cnpj,
            address=schema.address,
            commission=schema.commission,
            phone=schema.phone
        )
        return RealEstateDTO.model_validate(real_estate_model)

    def get_real_estate(self, real_estate_key: str) -> RealEstateDTO:
        real_estate_model = self.real_estate_repository.get_by_key(real_estate_key)
        if not real_estate_model:
            raise RealEstateNotFoundError(real_estate_key=real_estate_key)
        return RealEstateDTO.model_validate(real_estate_model)

    def get_paginated_real_estates(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search_term: str = None,
        name: str = None,
        cnpj: str = None,
        only_active_contracts: bool = False
    ) -> PaginatedResponseDTO[RealEstateDTO]:
        
        total_count, real_estate_models = self.real_estate_repository.get_paginated(
            skip=skip, 
            limit=limit, 
            search_term=search_term,
            name=name,
            cnpj=cnpj,
            only_active_contracts=only_active_contracts
        )
        
        real_estate_dtos = [RealEstateDTO.model_validate(e) for e in real_estate_models]
        
        return PaginatedResponseDTO(
            total=total_count,
            skip=skip,
            limit=limit,
            data=real_estate_dtos
        )

    def update_real_estate(self, real_estate_key: str, schema: RealEstateUpdateSchema) -> RealEstateDTO:
        real_estate_model = self.real_estate_repository.get_by_key(real_estate_key)
        if not real_estate_model:
            raise RealEstateNotFoundError(real_estate_key=real_estate_key)

        if real_estate_model.cnpj != schema.cnpj:
            existing = self.real_estate_repository.get_by_cnpj(schema.cnpj)
            if existing:
                raise RealEstateDuplicateCnpjError(cnpj=schema.cnpj)

        updated_model = self.real_estate_repository.update(
            real_estate_model=real_estate_model,
            name=schema.name,
            cnpj=schema.cnpj,
            address=schema.address,
            commission=schema.commission,
            phone=schema.phone
        )
        return RealEstateDTO.model_validate(updated_model)

    def delete_real_estate(self, real_estate_key: str) -> None:
        real_estate_model = self.real_estate_repository.get_by_key(real_estate_key)
        if not real_estate_model:
            raise RealEstateNotFoundError(real_estate_key=real_estate_key)
        self.real_estate_repository.delete(real_estate_model)