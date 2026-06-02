from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.models import RealEstateModel, ContractModel, ContractStatusModel
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

    def get_paginated(
        self,
        skip: int = 0,
        limit: int = 10,
        search_term: str | None = None,
        name: str | None = None,
        cnpj: str | None = None,
        only_active_contracts: bool = False
    ) -> tuple[int, list[RealEstateModel]]:
        
        query = self.db.query(RealEstateModel)

        if search_term:
            query = query.filter(
                or_(
                    RealEstateModel.name.ilike(f"%{search_term}%"),
                    RealEstateModel.cnpj.ilike(f"%{search_term}%")
                )
            )

        if name:
            query = query.filter(RealEstateModel.name.ilike(f"%{name}%"))
            
        if cnpj:
            query = query.filter(RealEstateModel.cnpj.ilike(f"%{cnpj}%"))

        if only_active_contracts:
            query = query.join(ContractModel, ContractModel.real_estate_id == RealEstateModel.id) \
                         .join(ContractStatusModel, ContractModel.status_id == ContractStatusModel.id) \
                         .filter(ContractStatusModel.enumerator == "active") \
                         .distinct()

        total_count = query.count()
        items = query.offset(skip).limit(limit).all()

        return total_count, items

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