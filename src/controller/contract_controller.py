from sqlalchemy.orm import Session
from src.repository.contract_repository import ContractRepository
from src.repository.contract_status_event_repository import ContractStatusEventRepository
from src.repository.property_repository import PropertyRepository
from src.repository.tenant_repository import TenantRepository
from src.repository.real_estate_repository import RealEstateRepository
from src.repository.guarantee_repository import GuaranteeRepository
from src.models import ContractStatusModel
from src.schemas.contract_schema import ContractSchema
from src.dto.contract_dto import ContractDTO
from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import ContractNotFoundError, ContractInvalidRelationError, InvalidEnumeratorError
from src.connectors.S3_storage_connector import S3StorageConnector

class ContractController:
    def __init__(self, db: Session):
        self.contract_repository = ContractRepository(db)
        self.contract_status_event_repository = ContractStatusEventRepository(db)
        self.property_repository = PropertyRepository(db)
        self.tenant_repository = TenantRepository(db)
        self.real_estate_repository = RealEstateRepository(db)
        self.guarantee_repository = GuaranteeRepository(db) 
        
        self.S3_connector = S3StorageConnector(bucket_name="contracts")

    def create_contract(self, schema: ContractSchema, current_user_data: dict) -> ContractDTO:
        contract_status_model = self.contract_repository.get_enumerator_model(ContractStatusModel, schema.status)
        if not contract_status_model:
            raise InvalidEnumeratorError(enumerator_name="Status do Contrato", invalid_value=schema.status)

        property_model = self.property_repository.get_by_key(schema.property_key)
        if not property_model:
            raise ContractInvalidRelationError(entity_name="Property", key=schema.property_key)

        tenant_model = self.tenant_repository.get_by_key(schema.tenant_key)
        if not tenant_model:
            raise ContractInvalidRelationError(entity_name="Tenant", key=schema.tenant_key)

        real_estate_model = None
        if schema.real_estate_key:
            real_estate_model = self.real_estate_repository.get_by_key(schema.real_estate_key)
            if not real_estate_model:
                raise ContractInvalidRelationError(entity_name="RealEstate", key=schema.real_estate_key)

        guarantee_model = None
        if schema.guarantee_key:
            guarantee_model = self.guarantee_repository.get_by_key(schema.guarantee_key)
            if not guarantee_model:
                raise ContractInvalidRelationError(entity_name="Guarantee", key=schema.guarantee_key)

        contract_model = self.contract_repository.create(
            rent_amount=schema.rent_amount,
            room_name=schema.room_name,
            status=contract_status_model,
            file_path=schema.file_path,
            property=property_model,
            tenant=tenant_model,
            real_estate=real_estate_model,
            guarantee=guarantee_model
        )
        
        self.contract_status_event_repository.create(
            contract=contract_model,
            status=contract_status_model,
            user_data=current_user_data
        )

        return ContractDTO.model_validate(contract_model)

    def get_contract(self, contract_key: str) -> ContractDTO:
        contract_model = self.contract_repository.get_by_key(contract_key)
        if not contract_model:
            raise ContractNotFoundError(contract_key=contract_key)
    
        contract_dto = ContractDTO.model_validate(contract_model)

        if contract_dto.file_path:
            contract_dto.file_path = self.S3_connector.get_signed_url(contract_dto.file_path)

        return contract_dto

    def update_contract(self, contract_key: str, schema: ContractSchema, current_user_data: dict) -> ContractDTO:
        contract_status_model = self.contract_repository.get_enumerator_model(ContractStatusModel, schema.status)
        if not contract_status_model:
            raise InvalidEnumeratorError(enumerator_name="Status do Contrato", invalid_value=schema.status)

        contract_model = self.contract_repository.get_by_key(contract_key)
        if not contract_model:
            raise ContractNotFoundError(contract_key=contract_key)

        property_model = self.property_repository.get_by_key(schema.property_key)
        if not property_model:
            raise ContractInvalidRelationError(entity_name="Property", key=schema.property_key)

        tenant_model = self.tenant_repository.get_by_key(schema.tenant_key)
        if not tenant_model:
            raise ContractInvalidRelationError(entity_name="Tenant", key=schema.tenant_key)

        real_estate_model = None
        if schema.real_estate_key:
            real_estate_model = self.real_estate_repository.get_by_key(schema.real_estate_key)
            if not real_estate_model:
                raise ContractInvalidRelationError(entity_name="RealEstate", key=schema.real_estate_key)

        new_guarantee_model = None
        if schema.guarantee_key:
            new_guarantee_model = self.guarantee_repository.get_by_key(schema.guarantee_key)
            if not new_guarantee_model:
                raise ContractInvalidRelationError(entity_name="Guarantee", key=schema.guarantee_key)

        if contract_model.guarantee and contract_model.guarantee.key != schema.guarantee_key:
            old_guarantee = contract_model.guarantee
            self.guarantee_repository.delete(old_guarantee) 

        old_status_enumerator = contract_model.status.enumerator

        updated_model = self.contract_repository.update(
            contract_model=contract_model,
            rent_amount=schema.rent_amount,
            room_name=schema.room_name,
            status=contract_status_model,
            file_path=schema.file_path,
            property=property_model,
            tenant=tenant_model,
            real_estate=real_estate_model,
            guarantee=new_guarantee_model
        )

        if old_status_enumerator != schema.status:
            self.contract_status_event_repository.create(
                contract=updated_model,
                status=contract_status_model,
                user_data=current_user_data
            )

        return ContractDTO.model_validate(updated_model)

    def delete_contract(self, contract_key: str) -> None:
        contract_model = self.contract_repository.get_by_key(contract_key)
        if not contract_model:
            raise ContractNotFoundError(contract_key=contract_key)
            
        if contract_model.guarantee:
            self.guarantee_repository.delete(contract_model.guarantee)
            
        self.contract_repository.delete(contract_model)

    def get_paginated_contracts(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search_term: str = None,
        room_name: str = None, 
        property_name: str = None, 
        tenant_name: str = None, 
        real_estate_name: str = None, 
        status: str = None
    ) -> PaginatedResponseDTO[ContractDTO]:
        
        total_count, contract_models = self.contract_repository.get_paginated(
            skip=skip, 
            limit=limit, 
            search_term=search_term,
            room_name=room_name, 
            property_name=property_name, 
            tenant_name=tenant_name, 
            real_estate_name=real_estate_name, 
            status=status
        )
        
        contracts = []
        for contract in contract_models:
            contract_dto = ContractDTO.model_validate(contract)
            if contract_dto.file_path:
                contract_dto.file_path = self.S3_connector.get_signed_url(contract_dto.file_path)
            contracts.append(contract_dto)
            
        return PaginatedResponseDTO(
            total=total_count,
            skip=skip,
            limit=limit,
            data=contracts
        )

    def upload_document(self, contract_key: str, file_bytes: bytes, content_type: str) -> ContractDTO:
        contract_model = self.contract_repository.get_by_key(contract_key)
        if not contract_model:
            raise ContractNotFoundError(contract_key=contract_key)
        
        extension = ".pdf" if "pdf" in content_type else ""
        file_name = f"{contract_key}_v1{extension}"

        file_url = self.S3_connector.upload_file(
            file_bytes=file_bytes,
            file_name=file_name,
            content_type=content_type
        )

        contract_model.file_path = file_url
        self.contract_repository.db.flush()

        return ContractDTO.model_validate(contract_model)