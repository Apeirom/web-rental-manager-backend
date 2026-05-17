from sqlalchemy.orm import Session
from src.models.guarantor_model import GuarantorModel

class GuarantorRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, document_number: str) -> GuarantorModel:
        guarantor = GuarantorModel(name=name, document_number=document_number)
        self.db.add(guarantor)
        self.db.commit()
        self.db.refresh(guarantor)
        return guarantor

    def get_by_key(self, guarantor_key: str) -> GuarantorModel | None:
        return self.db.query(GuarantorModel).filter(GuarantorModel.key == guarantor_key).first()

    def get_by_document(self, document_number: str) -> GuarantorModel | None:
        return self.db.query(GuarantorModel).filter(GuarantorModel.document_number == document_number).first()

    def get_all(self) -> list[GuarantorModel]:
        return self.db.query(GuarantorModel).all()

    def update(self, guarantor_model: GuarantorModel, name: str, document_number: str) -> GuarantorModel:
        guarantor_model.name = name
        guarantor_model.document_number = document_number
        self.db.commit()
        self.db.refresh(guarantor_model)
        return guarantor_model

    def delete(self, guarantor_model: GuarantorModel) -> None:
        self.db.delete(guarantor_model)
        self.db.commit()