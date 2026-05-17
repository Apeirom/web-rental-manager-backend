from sqlalchemy.orm import Session
from src.repository.guarantor_repository import GuarantorRepository
from src.schemas.guarantor_schema import GuarantorCreateSchema, GuarantorUpdateSchema
from src.dto.guarantor_dto import GuarantorDTO
from src.errors.custom_errors import GuarantorNotFoundError, GuarantorDuplicateDocumentError

class GuarantorController:
    def __init__(self, db: Session):
        self.repository = GuarantorRepository(db)

    def create_guarantor(self, schema: GuarantorCreateSchema) -> GuarantorDTO:
        existing = self.repository.get_by_document(schema.document_number)
        if existing:
            raise GuarantorDuplicateDocumentError(document_number=schema.document_number)

        guarantor_model = self.repository.create(
            name=schema.name,
            document_number=schema.document_number
        )
        return GuarantorDTO.model_validate(guarantor_model)

    def get_guarantor(self, guarantor_key: str) -> GuarantorDTO:
        guarantor_model = self.repository.get_by_key(guarantor_key)
        if not guarantor_model:
            raise GuarantorNotFoundError(guarantor_key=guarantor_key)
        return GuarantorDTO.model_validate(guarantor_model)

    def get_all_guarantors(self) -> list[GuarantorDTO]:
        entities = self.repository.get_all()
        return [GuarantorDTO.model_validate(e) for e in entities]

    def update_guarantor(self, guarantor_key: str, schema: GuarantorUpdateSchema) -> GuarantorDTO:
        guarantor_model = self.repository.get_by_key(guarantor_key)
        if not guarantor_model:
            raise GuarantorNotFoundError(guarantor_key=guarantor_key)

        if guarantor_model.document_number != schema.document_number:
            existing = self.repository.get_by_document(schema.document_number)
            if existing:
                raise GuarantorDuplicateDocumentError(document_number=schema.document_number)

        updated_model = self.repository.update(
            guarantor_model=guarantor_model,
            name=schema.name,
            document_number=schema.document_number
        )
        return GuarantorDTO.model_validate(updated_model)

    def delete_guarantor(self, guarantor_key: str) -> None:
        guarantor_model = self.repository.get_by_key(guarantor_key)
        if not guarantor_model:
            raise GuarantorNotFoundError(guarantor_key=guarantor_key)
        self.repository.delete(guarantor_model)