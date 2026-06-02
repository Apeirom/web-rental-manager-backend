from sqlalchemy.orm import Session
from src.repository.guarantor_repository import GuarantorRepository
from src.schemas.guarantor_schema import GuarantorCreateSchema, GuarantorUpdateSchema
from src.dto.guarantor_dto import GuarantorDTO
from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import GuarantorNotFoundError, GuarantorDuplicateDocumentError

class GuarantorController:
    def __init__(self, db: Session):
        self.guarantor_repository = GuarantorRepository(db)

    def create_guarantor(self, schema: GuarantorCreateSchema) -> GuarantorDTO:
        existing = self.guarantor_repository.get_by_document(schema.document_number)
        if existing:
            raise GuarantorDuplicateDocumentError(document_number=schema.document_number)

        guarantor_model = self.guarantor_repository.create(
            name=schema.name,
            document_number=schema.document_number
        )
        return GuarantorDTO.model_validate(guarantor_model)

    def get_guarantor(self, guarantor_key: str) -> GuarantorDTO:
        guarantor_model = self.guarantor_repository.get_by_key(guarantor_key)
        if not guarantor_model:
            raise GuarantorNotFoundError(guarantor_key=guarantor_key)
        return GuarantorDTO.model_validate(guarantor_model)

    def get_paginated_guarantors(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search_term: str = None,
        name: str = None,
        document_number: str = None,
        only_active_contracts: bool = False
    ) -> PaginatedResponseDTO[GuarantorDTO]:
        
        total_count, guarantor_models = self.guarantor_repository.get_paginated(
            skip=skip, 
            limit=limit, 
            search_term=search_term,
            name=name,
            document_number=document_number,
            only_active_contracts=only_active_contracts
        )
        
        guarantor_dtos = [GuarantorDTO.model_validate(e) for e in guarantor_models]
        
        return PaginatedResponseDTO(
            total=total_count,
            skip=skip,
            limit=limit,
            data=guarantor_dtos
        )

    def update_guarantor(self, guarantor_key: str, schema: GuarantorUpdateSchema) -> GuarantorDTO:
        guarantor_model = self.guarantor_repository.get_by_key(guarantor_key)
        if not guarantor_model:
            raise GuarantorNotFoundError(guarantor_key=guarantor_key)

        if guarantor_model.document_number != schema.document_number:
            existing = self.guarantor_repository.get_by_document(schema.document_number)
            if existing:
                raise GuarantorDuplicateDocumentError(document_number=schema.document_number)

        updated_model = self.guarantor_repository.update(
            guarantor_model=guarantor_model,
            name=schema.name,
            document_number=schema.document_number
        )
        return GuarantorDTO.model_validate(updated_model)

    def delete_guarantor(self, guarantor_key: str) -> None:
        guarantor_model = self.guarantor_repository.get_by_key(guarantor_key)
        if not guarantor_model:
            raise GuarantorNotFoundError(guarantor_key=guarantor_key)
        self.guarantor_repository.delete(guarantor_model)