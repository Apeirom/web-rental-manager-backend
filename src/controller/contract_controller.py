from sqlalchemy.orm import Session
from src.repository.enumerator_repository import EnumeratorRepository
from src.repository.contract_repository import ContractRepository
from src.repository.property_repository import PropertyRepository
from src.repository.tenant_repository import TenantRepository
from src.repository.real_estate_repository import RealEstateRepository
from src.repository.guarantor_repository import GuarantorRepository
from src.repository.bail_insurance_repository import BailInsuranceRepository
from src.models.guarantee_type_model import GuaranteeTypeModel
from src.models.contract_status_model import ContractStatusModel
from src.schemas.contract_schema import ContractCreateSchema, ContractUpdateSchema
from src.dto.contract_dto import ContractDTO
from src.errors.custom_errors import ContractNotFoundError, ContractInvalidRelationError, InvalidEnumeratorError
from src.connectors.supabase_storage_connector import SupabaseStorage

class ContractController:
    def __init__(self, db: Session):
        self.contract_repository = ContractRepository(db)
        self.property_repository = PropertyRepository(db)
        self.tenant_repository = TenantRepository(db)
        self.real_estate_repository = RealEstateRepository(db)
        self.guarantor_repository = GuarantorRepository(db)
        self.bail_insurance_repository = BailInsuranceRepository(db)
        self.enumerator_repository = EnumeratorRepository(db)

    def create_contract(self, schema: ContractCreateSchema) -> ContractDTO:
        guarantee_type_model = self.enumerator_repository.get_enumerator_model(GuaranteeTypeModel, schema.guarantee_type)
        if not guarantee_type_model:
            raise InvalidEnumeratorError(enumerator_name="Garantia", invalid_value=schema.guarantee_type)

        contract_status_model = self.enumerator_repository.get_enumerator_model(ContractStatusModel, schema.status)
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

        guarantor_model = None
        if schema.guarantor_key:
            guarantor_model = self.guarantor_repository.get_by_key(schema.guarantor_key)
            if not guarantor_model:
                raise ContractInvalidRelationError(entity_name="Guarantor", key=schema.guarantor_key)

        bail_insurance_model = None
        if schema.bail_insurance_key:
            bail_insurance_model = self.bail_insurance_repository.get_by_key(schema.bail_insurance_key)
            if not bail_insurance_model:
                raise ContractInvalidRelationError(entity_name="BailInsurance", key=schema.bail_insurance_key)

        contract_model = self.contract_repository.create(
            guarantee_type=guarantee_type_model,
            rental_deposit=schema.rental_deposit,
            rent_amount=schema.rent_amount,
            room_name=schema.room_name,
            status=contract_status_model,
            file_path=schema.file_path,
            property=property_model,
            tenant=tenant_model,
            real_estate=real_estate_model,
            guarantor=guarantor_model,
            bail_insurance=bail_insurance_model
        )
        return ContractDTO.model_validate(contract_model)

    def get_contract(self, contract_key: str) -> ContractDTO:
        contract_model = self.contract_repository.get_by_key(contract_key)
        if not contract_model:
            raise ContractNotFoundError(contract_key=contract_key)
        return ContractDTO.model_validate(contract_model)

    def get_all_contracts(self) -> list[ContractDTO]:
        entities = self.contract_repository.get_all()
        return [ContractDTO.model_validate(e) for e in entities]

    def update_contract(self, contract_key: str, schema: ContractUpdateSchema) -> ContractDTO:
        guarantee_type_model = self.enumerator_repository.get_enumerator_model(GuaranteeTypeModel, schema.guarantee_type)
        if not guarantee_type_model:
            raise InvalidEnumeratorError(enumerator_name="Garantia", invalid_value=schema.guarantee_type)

        contract_status_model = self.enumerator_repository.get_enumerator_model(ContractStatusModel, schema.status)
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

        guarantor_model = None
        if schema.guarantor_key:
            guarantor_model = self.guarantor_repository.get_by_key(schema.guarantor_key)
            if not guarantor_model:
                raise ContractInvalidRelationError(entity_name="Guarantor", key=schema.guarantor_key)

        bail_insurance_model = None
        if schema.bail_insurance_key:
            bail_insurance_model = self.bail_insurance_repository.get_by_key(schema.bail_insurance_key)
            if not bail_insurance_model:
                raise ContractInvalidRelationError(entity_name="BailInsurance", key=schema.bail_insurance_key)

        updated_model = self.contract_repository.update(
            contract_model=contract_model,
            guarantee_type=guarantee_type_model,
            rental_deposit=schema.rental_deposit,
            rent_amount=schema.rent_amount,
            room_name=schema.room_name,
            status=contract_status_model,
            file_path=schema.file_path,
            property=property_model,
            tenant=tenant_model,
            real_estate=real_estate_model,
            guarantor=guarantor_model,
            bail_insurance=bail_insurance_model
        )
        return ContractDTO.model_validate(updated_model)

    def delete_contract(self, contract_key: str) -> None:
        contract_model = self.contract_repository.get_by_key(contract_key)
        if not contract_model:
            raise ContractNotFoundError(contract_key=contract_key)
        self.contract_repository.delete(contract_model)

    def upload_document(self, contract_key: str, file_bytes: bytes, content_type: str) -> ContractDTO:
        contract_model = self.contract_repository.get_by_key(contract_key)
        if not contract_model:
            raise ContractNotFoundError(contract_key=contract_key)

        storage = SupabaseStorage(bucket_name="contracts")
        
        extension = ".pdf" if "pdf" in content_type else ""
        file_name = f"{contract_key}_v1{extension}"

        file_url = storage.upload_file(
            file_bytes=file_bytes,
            file_name=file_name,
            content_type=content_type
        )

        contract_model.file_path = file_url
        self.contract_repository.db.commit()
        self.contract_repository.db.refresh(contract_model)

        return ContractDTO.model_validate(contract_model)