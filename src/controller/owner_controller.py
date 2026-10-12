from sqlalchemy.orm import Session
from src.repository.owner_repository import OwnerRepository
from src.schemas.owner_schema import OwnerCreateSchema, OwnerUpdateSchema
from src.dto.owner_dto import OwnerDTO
from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import OwnerNotFoundError

class OwnerController:
    def __init__(self, db: Session):
        self.owner_repository = OwnerRepository(db)

    def create_owner(self, schema: OwnerCreateSchema) -> OwnerDTO:
        owner_model = self.owner_repository.create(
            name=schema.name,
            document_number=schema.document_number
        )
        return OwnerDTO.model_validate(owner_model)

    def get_owner(self, owner_key: str) -> OwnerDTO:
        owner_model = self.owner_repository.get_by_key(owner_key)
        if not owner_model:
            raise OwnerNotFoundError(owner_key=owner_key)
        return OwnerDTO.model_validate(owner_model)

    def get_paginated_owners(self, skip: int = 0, limit: int = 10, search_term: str = None) -> PaginatedResponseDTO[OwnerDTO]:
        total_count, owner_models = self.owner_repository.get_paginated(skip, limit, search_term)
        owner_dtos = [OwnerDTO.model_validate(o) for o in owner_models]
        return PaginatedResponseDTO(total=total_count, skip=skip, limit=limit, data=owner_dtos)

    def update_owner(self, owner_key: str, schema: OwnerUpdateSchema) -> OwnerDTO:
        owner_model = self.owner_repository.get_by_key(owner_key)
        if not owner_model:
            raise OwnerNotFoundError(owner_key=owner_key)
            
        updated_model = self.owner_repository.update(
            owner_model=owner_model,
            name=schema.name,
            document_number=schema.document_number
        )
        return OwnerDTO.model_validate(updated_model)

    def delete_owner(self, owner_key: str) -> None:
        owner_model = self.owner_repository.get_by_key(owner_key)
        if not owner_model:
            raise OwnerNotFoundError(owner_key=owner_key)

        self.owner_repository.delete(owner_model)