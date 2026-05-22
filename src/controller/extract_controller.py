from sqlalchemy.orm import Session
from src.repository.extract_repository import ExtractRepository
from src.repository.contract_repository import ContractRepository
from src.schemas.extract_schema import ExtractCreateSchema, ExtractUpdateSchema
from src.dto.extract_dto import ExtractDTO
from src.errors.custom_errors import ExtractNotFoundError, ExtractInvalidRelationError
from src.connectors.supabase_storage_connector import SupabaseStorage

class ExtractController:
    def __init__(self, db: Session):
        self.repository = ExtractRepository(db)
        self.contract_repo = ContractRepository(db)

    def _calculate_financials(self, schema, contract_model):
        commission_rate = 0.0
        if contract_model.real_estate:
            commission_rate = contract_model.real_estate.commission

        admin_fee = (schema.rent_amount + schema.penalty) * commission_rate

        total_revenues = (
            schema.rent_amount +
            schema.iptu +
            schema.water +
            schema.maintenance +
            schema.agreement +
            schema.penalty +
            schema.interest +
            schema.other_revenues
        )

        net_transfer = total_revenues - admin_fee - schema.bank_fee

        return admin_fee, net_transfer

    def create_extract(self, schema: ExtractCreateSchema) -> ExtractDTO:
        contract_model = self.contract_repo.get_by_key(schema.contract_key)
        if not contract_model:
            raise ExtractInvalidRelationError(entity_name="Contract", key=schema.contract_key)

        admin_fee, net_transfer = self._calculate_financials(schema, contract_model)

        extract_model = self.repository.create(
            month_ref=schema.month_ref,
            year_ref=schema.year_ref,
            rent_amount=schema.rent_amount,
            iptu=schema.iptu,
            water=schema.water,
            maintenance=schema.maintenance,
            agreement=schema.agreement,
            penalty=schema.penalty,
            interest=schema.interest,
            other_revenues=schema.other_revenues,
            bank_fee=schema.bank_fee,
            administration_fee=admin_fee,
            net_transfer=net_transfer,
            receipt_path=schema.receipt_path,
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

        admin_fee, net_transfer = self._calculate_financials(schema, contract_model)

        updated_model = self.repository.update(
            extract_model=extract_model,
            month_ref=schema.month_ref,
            year_ref=schema.year_ref,
            rent_amount=schema.rent_amount,
            iptu=schema.iptu,
            water=schema.water,
            maintenance=schema.maintenance,
            agreement=schema.agreement,
            penalty=schema.penalty,
            interest=schema.interest,
            other_revenues=schema.other_revenues,
            bank_fee=schema.bank_fee,
            administration_fee=admin_fee,
            net_transfer=net_transfer,
            receipt_path=schema.receipt_path,
            contract_id=contract_model.id
        )
        return ExtractDTO.model_validate(updated_model)

    def delete_extract(self, extract_key: str) -> None:
        extract_model = self.repository.get_by_key(extract_key)
        if not extract_model:
            raise ExtractNotFoundError(extract_key=extract_key)
        self.repository.delete(extract_model)

    def upload_receipt(self, extract_key: str, file_bytes: bytes, content_type: str) -> ExtractDTO:
        extract_model = self.repository.get_by_key(extract_key)
        if not extract_model:
            raise ExtractNotFoundError(extract_key=extract_key)

        storage = SupabaseStorage(bucket_name="extracts")
        
        extension = ".pdf" if "pdf" in content_type else ""
        file_name = f"{extract_key}_v1{extension}"

        file_url = storage.upload_file(
            file_bytes=file_bytes,
            file_name=file_name,
            content_type=content_type
        )

        extract_model.receipt_path = file_url
        self.repository.db.commit()
        self.repository.db.refresh(extract_model)

        return ExtractDTO.model_validate(extract_model)