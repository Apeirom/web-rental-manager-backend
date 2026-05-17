from sqlalchemy.orm import Session
from src.repository.extract_repository import ExtractRepository
from src.repository.contract_repository import ContractRepository
from src.schemas.extract_schema import ExtractCreateSchema, ExtractUpdateSchema
from src.dto.extract_dto import ExtractDTO
from src.errors.custom_errors import ExtractNotFoundError, ExtractInvalidRelationError

class ExtractController:
    def __init__(self, db: Session):
        self.repository = ExtractRepository(db)
        self.contract_repo = ContractRepository(db)

    def create_extract(self, schema: ExtractCreateSchema) -> ExtractDTO:
        contract_model = self.contract_repo.get_by_key(schema.contract_key)
        if not contract_model:
            raise ExtractInvalidRelationError(entity_name="Contract", key=schema.contract_key)

        extract_model = self.repository.create(
            month_ref=schema.month_ref,
            year_ref=schema.year_ref,
            rent_amount=schema.rent_amount,
            receipt_path=schema.receipt_path,
            iptu=schema.iptu,
            water=schema.water,
            agreement=schema.agreement,
            contract_id=contract_model.id
        )
        return ExtractDTO.model_validate(extract_model)

    def get_extract(self, extract_key: str) -> ExtractDTO:
        extract_model = self.repository.get_by_key(extract_key)
        if not extract_model:
            raise ExtractNotFoundError(extract_key=extract_key)
        return ExtractDTO.model_validate(extract_model)

    def get_all_extracts(self) -> list[ExtractDTO]:
        entities = self.repository.get_all()
        return [ExtractDTO.model_validate(e) for e in entities]

    def update_extract(self, extract_key: str, schema: ExtractUpdateSchema) -> ExtractDTO:
        extract_model = self.repository.get_by_key(extract_key)
        if not extract_model:
            raise ExtractNotFoundError(extract_key=extract_key)

        contract_model = self.contract_repo.get_by_key(schema.contract_key)
        if not contract_model:
            raise ExtractInvalidRelationError(entity_name="Contract", key=schema.contract_key)

        updated_model = self.repository.update(
            extract_model=extract_model,
            month_ref=schema.month_ref,
            year_ref=schema.year_ref,
            rent_amount=schema.rent_amount,
            receipt_path=schema.receipt_path,
            iptu=schema.iptu,
            water=schema.water,
            agreement=schema.agreement,
            contract_id=contract_model.id
        )
        return ExtractDTO.model_validate(updated_model)

    def delete_extract(self, extract_key: str) -> None:
        extract_model = self.repository.get_by_key(extract_key)
        if not extract_model:
            raise ExtractNotFoundError(extract_key=extract_key)
        self.repository.delete(extract_model)