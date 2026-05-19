from sqlalchemy.orm import Session
from src.models.contract_model import ContractModel
from src.models.guarantee_type_model import GuaranteeTypeModel
from src.models.contract_status_model import ContractStatusModel
from src.models.property_model import PropertyModel
from src.models.tenant_model import TenantModel
from src.models.real_estate_model import RealEstateModel
from src.models.guarantor_model import GuarantorModel
from src.models.bail_insurance_model import BailInsuranceModel

class ContractRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, guarantee_type: GuaranteeTypeModel, rental_deposit: float, rent_amount: float, room_name: str | None, status: ContractStatusModel, file_path: str | None, property: PropertyModel, tenant: TenantModel, real_estate: RealEstateModel | None, guarantor: GuarantorModel | None, bail_insurance: BailInsuranceModel | None) -> ContractModel:
        contract = ContractModel(
            guarantee_type=guarantee_type,
            rental_deposit=rental_deposit,
            rent_amount=rent_amount,
            room_name=room_name,
            status=status,
            file_path=file_path,
            property=property,
            tenant=tenant,
            real_estate=real_estate,
            guarantor=guarantor,
            bail_insurance=bail_insurance
        )
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def get_by_key(self, contract_key: str) -> ContractModel | None:
        return self.db.query(ContractModel).filter(ContractModel.key == contract_key).first()

    def get_all(self) -> list[ContractModel]:
        return self.db.query(ContractModel).all()

    def update(self, contract_model: ContractModel, guarantee_type: GuaranteeTypeModel, rental_deposit: float, rent_amount: float, room_name: str | None, status: ContractStatusModel, file_path: str | None, property: PropertyModel, tenant: TenantModel, real_estate: RealEstateModel | None, guarantor: GuarantorModel | None, bail_insurance: BailInsuranceModel | None) -> ContractModel:
        contract_model.guarantee_type = guarantee_type
        contract_model.rental_deposit = rental_deposit
        contract_model.rent_amount = rent_amount
        contract_model.room_name = room_name
        contract_model.status = status
        contract_model.file_path = file_path
        contract_model.property = property
        contract_model.tenant = tenant
        contract_model.real_estate = real_estate
        contract_model.guarantor = guarantor
        contract_model.bail_insurance = bail_insurance
        self.db.commit()
        self.db.refresh(contract_model)
        return contract_model

    def delete(self, contract_model: ContractModel) -> None:
        self.db.delete(contract_model)
        self.db.commit()