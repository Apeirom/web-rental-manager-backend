from sqlalchemy.orm import Session
from src.repository.contract_repository import ContractRepository
from src.repository.property_repository import PropertyRepository
from src.repository.tenant_repository import TenantRepository
from src.repository.real_estate_repository import RealEstateRepository
from src.repository.guarantor_repository import GuarantorRepository
from src.repository.bail_insurance_repository import BailInsuranceRepository
from src.schemas.contract_schema import ContractCreateSchema, ContractUpdateSchema
from src.dto.contract_dto import ContractDTO
from src.errors.custom_errors import ContractNotFoundError, ContractInvalidRelationError

class ContractController:
    def __init__(self, db: Session):
        self.contract_repository = ContractRepository(db)
        self.property_repository = PropertyRepository(db)
        self.tenant_repository = TenantRepository(db)
        self.real_estate_repository = RealEstateRepository(db)
        self.guarantor_repository = GuarantorRepository(db)
        self.bail_insurance_repository = BailInsuranceRepository(db)

    def create_contract(self, schema: ContractCreateSchema) -> ContractDTO:
        property_model = self.property_repository.get_by_key(schema.property_key)
        if not property_model:
            raise ContractInvalidRelationError(entity_name="Property", key=schema.property_key)

        tenant_model = self.tenant_repository.get_by_key(schema.tenant_key)
        if not tenant_model:
            raise ContractInvalidRelationError(entity_name="Tenant", key=schema.tenant_key)

        real_estate_id = None
        if schema.real_estate_key:
            real_estate_model = self.real_estate_repository.get_by_key(schema.real_estate_key)
            if not real_estate_model:
                raise ContractInvalidRelationError(entity_name="RealEstate", key=schema.real_estate_key)
            real_estate_id = real_estate_model.id

        guarantor_id = None
        if schema.guarantor_key:
            guarantor_model = self.guarantor_repository.get_by_key(schema.guarantor_key)
            if not guarantor_model:
                raise ContractInvalidRelationError(entity_name="Guarantor", key=schema.guarantor_key)
            guarantor_id = guarantor_model.id

        bail_insurance_id = None
        if schema.bail_insurance_key:
            bail_insurance_model = self.bail_insurance_repository.get_by_key(schema.bail_insurance_key)
            if not bail_insurance_model:
                raise ContractInvalidRelationError(entity_name="BailInsurance", key=schema.bail_insurance_key)
            bail_insurance_id = bail_insurance_model.id

        contract_model = self.contract_repository.create(
            guarantee=schema.guarantee,
            rental_deposit=schema.rental_deposit,
            rent_amount=schema.rent_amount,
            room_name=schema.room_name,
            acting=schema.acting,
            file_path=schema.file_path,
            property_id=property_model.id,
            tenant_id=tenant_model.id,
            real_estate_id=real_estate_id,
            guarantor_id=guarantor_id,
            bail_insurance_id=bail_insurance_id
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
        contract_model = self.contract_repository.get_by_key(contract_key)
        if not contract_model:
            raise ContractNotFoundError(contract_key=contract_key)

        property_model = self.property_repository.get_by_key(schema.property_key)
        if not property_model:
            raise ContractInvalidRelationError(entity_name="Property", key=schema.property_key)

        tenant_model = self.tenant_repository.get_by_key(schema.tenant_key)
        if not tenant_model:
            raise ContractInvalidRelationError(entity_name="Tenant", key=schema.tenant_key)

        real_estate_id = None
        if schema.real_estate_key:
            real_estate_model = self.real_estate_repository.get_by_key(schema.real_estate_key)
            if not real_estate_model:
                raise ContractInvalidRelationError(entity_name="RealEstate", key=schema.real_estate_key)
            real_estate_id = real_estate_model.id

        guarantor_id = None
        if schema.guarantor_key:
            guarantor_model = self.guarantor_repository.get_by_key(schema.guarantor_key)
            if not guarantor_model:
                raise ContractInvalidRelationError(entity_name="Guarantor", key=schema.guarantor_key)
            guarantor_id = guarantor_model.id

        bail_insurance_id = None
        if schema.bail_insurance_key:
            bail_insurance_model = self.bail_insurance_repository.get_by_key(schema.bail_insurance_key)
            if not bail_insurance_model:
                raise ContractInvalidRelationError(entity_name="BailInsurance", key=schema.bail_insurance_key)
            bail_insurance_id = bail_insurance_model.id

        updated_model = self.contract_repository.update(
            contract_model=contract_model,
            guarantee=schema.guarantee,
            rental_deposit=schema.rental_deposit,
            rent_amount=schema.rent_amount,
            room_name=schema.room_name,
            acting=schema.acting,
            file_path=schema.file_path,
            property_id=property_model.id,
            tenant_id=tenant_model.id,
            real_estate_id=real_estate_id,
            guarantor_id=guarantor_id,
            bail_insurance_id=bail_insurance_id
        )
        return ContractDTO.model_validate(updated_model)

    def delete_contract(self, contract_key: str) -> None:
        contract_model = self.contract_repository.get_by_key(contract_key)
        if not contract_model:
            raise ContractNotFoundError(contract_key=contract_key)
        self.contract_repository.delete(contract_model)