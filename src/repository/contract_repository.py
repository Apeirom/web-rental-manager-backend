from sqlalchemy.orm import Session
from src.models.contract_model import ContractModel

class ContractRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, guarantee: str, rental_deposit: float, rent_amount: float, room_name: str | None, acting: str, file_path: str | None, property_id: int, tenant_id: int, real_estate_id: int | None, guarantor_id: int | None, bail_insurance_id: int | None) -> ContractModel:
        contract = ContractModel(
            guarantee=guarantee,
            rental_deposit=rental_deposit,
            rent_amount=rent_amount,
            room_name=room_name,
            acting=acting,
            file_path=file_path,
            property_id=property_id,
            tenant_id=tenant_id,
            real_estate_id=real_estate_id,
            guarantor_id=guarantor_id,
            bail_insurance_id=bail_insurance_id
        )
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def get_by_key(self, contract_key: str) -> ContractModel | None:
        return self.db.query(ContractModel).filter(ContractModel.key == contract_key).first()

    def get_all(self) -> list[ContractModel]:
        return self.db.query(ContractModel).all()

    def update(self, contract_model: ContractModel, guarantee: str, rental_deposit: float, rent_amount: float, room_name: str | None, acting: str, file_path: str | None, property_id: int, tenant_id: int, real_estate_id: int | None, guarantor_id: int | None, bail_insurance_id: int | None) -> ContractModel:
        contract_model.guarantee = guarantee
        contract_model.rental_deposit = rental_deposit
        contract_model.rent_amount = rent_amount
        contract_model.room_name = room_name
        contract_model.acting = acting
        contract_model.file_path = file_path
        contract_model.property_id = property_id
        contract_model.tenant_id = tenant_id
        contract_model.real_estate_id = real_estate_id
        contract_model.guarantor_id = guarantor_id
        contract_model.bail_insurance_id = bail_insurance_id
        self.db.commit()
        self.db.refresh(contract_model)
        return contract_model

    def delete(self, contract_model: ContractModel) -> None:
        self.db.delete(contract_model)
        self.db.commit()