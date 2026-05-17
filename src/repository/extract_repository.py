from sqlalchemy.orm import Session
from src.models.extract_model import ExtractModel

class ExtractRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, month_ref: int, year_ref: int, rent_amount: float, receipt_path: str | None, iptu: float, water: float, agreement: float, contract_id: int) -> ExtractModel:
        extract = ExtractModel(
            month_ref=month_ref,
            year_ref=year_ref,
            rent_amount=rent_amount,
            receipt_path=receipt_path,
            iptu=iptu,
            water=water,
            agreement=agreement,
            contract_id=contract_id
        )
        self.db.add(extract)
        self.db.commit()
        self.db.refresh(extract)
        return extract

    def get_by_key(self, extract_key: str) -> ExtractModel | None:
        return self.db.query(ExtractModel).filter(ExtractModel.key == extract_key).first()

    def get_all(self) -> list[ExtractModel]:
        return self.db.query(ExtractModel).all()

    def update(self, extract_model: ExtractModel, month_ref: int, year_ref: int, rent_amount: float, receipt_path: str | None, iptu: float, water: float, agreement: float, contract_id: int) -> ExtractModel:
        extract_model.month_ref = month_ref
        extract_model.year_ref = year_ref
        extract_model.rent_amount = rent_amount
        extract_model.receipt_path = receipt_path
        extract_model.iptu = iptu
        extract_model.water = water
        extract_model.agreement = agreement
        extract_model.contract_id = contract_id
        self.db.commit()
        self.db.refresh(extract_model)
        return extract_model

    def delete(self, extract_model: ExtractModel) -> None:
        self.db.delete(extract_model)
        self.db.commit()