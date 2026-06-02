from sqlalchemy.orm import Session
from src.repository.extract_repository import ExtractRepository
from src.repository.contract_repository import ContractRepository
from src.schemas.extract_schema import ExtractCreateSchema, ExtractUpdateSchema
from src.dto.extract_dto import ExtractDTO
from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import ExtractNotFoundError, ExtractInvalidRelationError
from src.connectors.S3_storage_connector import S3StorageConnector

class ExtractController:
    def __init__(self, db: Session):
        self.extract_repository = ExtractRepository(db)
        self.contract_repo = ContractRepository(db)
        self.S3_connector = S3StorageConnector(bucket_name="extracts")

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

        extract_model = self.extract_repository.create(
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
            file_path=schema.file_path,
            contract_id=contract_model.id
        )
        return ExtractDTO.model_validate(extract_model)

    def get_extract(self, extract_key: str) -> ExtractDTO:
        extract_model = self.extract_repository.get_by_key(extract_key)
        if not extract_model:
            raise ExtractNotFoundError(extract_key=extract_key)
        
        extract_dto = ExtractDTO.model_validate(extract_model)
        if extract_dto.file_path:
            extract_dto.file_path = self.S3_connector.get_signed_url(extract_dto.file_path)
        return extract_dto

    def get_paginated_extracts(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search_term: str = None,
        only_active_contracts: bool = False
    ) -> PaginatedResponseDTO[ExtractDTO]:
        
        total_count, extract_models = self.extract_repository.get_paginated(
            skip=skip, 
            limit=limit, 
            search_term=search_term,
            only_active_contracts=only_active_contracts
        )

        extracts = []
        for extract in extract_models:
            extract_dto = ExtractDTO.model_validate(extract)
            if extract_dto.file_path:
                extract_dto.file_path = self.S3_connector.get_signed_url(extract_dto.file_path)
            extracts.append(extract_dto)

        return PaginatedResponseDTO(
            total=total_count,
            skip=skip,
            limit=limit,
            data=extracts
        )

    def update_extract(self, extract_key: str, schema: ExtractUpdateSchema) -> ExtractDTO:
        extract_model = self.extract_repository.get_by_key(extract_key)
        if not extract_model:
            raise ExtractNotFoundError(extract_key=extract_key)

        contract_model = self.contract_repo.get_by_key(schema.contract_key)
        if not contract_model:
            raise ExtractInvalidRelationError(entity_name="Contract", key=schema.contract_key)

        admin_fee, net_transfer = self._calculate_financials(schema, contract_model)

        updated_model = self.extract_repository.update(
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
            file_path=schema.file_path,
            contract_id=contract_model.id
        )
        return ExtractDTO.model_validate(updated_model)

    def delete_extract(self, extract_key: str) -> None:
        extract_model = self.extract_repository.get_by_key(extract_key)
        if not extract_model:
            raise ExtractNotFoundError(extract_key=extract_key)
        self.extract_repository.delete(extract_model)

    def upload_receipt(self, extract_key: str, file_bytes: bytes, content_type: str) -> ExtractDTO:
        extract_model = self.extract_repository.get_by_key(extract_key)
        if not extract_model:
            raise ExtractNotFoundError(extract_key=extract_key)
        
        extension = ".pdf" if "pdf" in content_type else ""
        file_name = f"{extract_key}_v1{extension}"

        file_url = self.S3_connector.upload_file(
            file_bytes=file_bytes,
            file_name=file_name,
            content_type=content_type
        )

        extract_model.file_path = file_url
        self.extract_repository.db.flush()

        return ExtractDTO.model_validate(extract_model)