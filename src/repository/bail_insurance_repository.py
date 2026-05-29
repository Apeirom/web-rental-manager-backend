from sqlalchemy.orm import Session
from src.models.bail_insurance_model import BailInsuranceModel
from src.repository.base_repository import BaseRepository

class BailInsuranceRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, value: float, validity: str, insurance_company: str) -> BailInsuranceModel:
        bail_insurance = BailInsuranceModel(
            value=value,
            validity=validity,
            insurance_company=insurance_company
        )
        self.db.add(bail_insurance)
        self.db.flush()
        return bail_insurance

    def get_by_key(self, bail_insurance_key: str) -> BailInsuranceModel | None:
        return self.db.query(BailInsuranceModel).filter(BailInsuranceModel.key == bail_insurance_key).first()

    def get_all(self) -> list[BailInsuranceModel]:
        return self.db.query(BailInsuranceModel).all()

    def update(self, bail_insurance_model: BailInsuranceModel, value: float, validity: str, insurance_company: str) -> BailInsuranceModel:
        bail_insurance_model.value = value
        bail_insurance_model.validity = validity
        bail_insurance_model.insurance_company = insurance_company
        self.db.flush()
        return bail_insurance_model

    def delete(self, bail_insurance_model: BailInsuranceModel) -> None:
        self.db.delete(bail_insurance_model)