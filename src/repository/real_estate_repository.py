from sqlalchemy.orm import Session
from src.models.real_estate_model import RealEstateModel
from src.repository.base_repository import BaseRepository 


class RealEstateRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, name: str, cnpj: str, address: str, commission: float, phone: str) -> RealEstateModel:
        real_estate = RealEstateModel(
            name=name,
            cnpj=cnpj,
            address=address,
            commission=commission,
            phone=phone
        )
        self.db.add(real_estate)
        self.db.flush()
        return real_estate

    def get_by_key(self, real_estate_key: str) -> RealEstateModel | None:
        return self.db.query(RealEstateModel).filter(RealEstateModel.key == real_estate_key).first()

    def get_by_cnpj(self, cnpj: str) -> RealEstateModel | None:
        return self.db.query(RealEstateModel).filter(RealEstateModel.cnpj == cnpj).first()

    def get_all(self) -> list[RealEstateModel]:
        return self.db.query(RealEstateModel).all()

    def update(self, real_estate_model: RealEstateModel, name: str, cnpj: str, address: str, commission: float, phone: str) -> RealEstateModel:
        real_estate_model.name = name
        real_estate_model.cnpj = cnpj
        real_estate_model.address = address
        real_estate_model.commission = commission
        real_estate_model.phone = phone
        self.db.flush()
        return real_estate_model

    def delete(self, real_estate_model: RealEstateModel) -> None:
        self.db.delete(real_estate_model)
        self.db.flush()