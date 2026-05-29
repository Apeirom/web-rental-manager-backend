from sqlalchemy.orm import Session
from src.models.guarantor_model import GuarantorModel
from src.repository.base_repository import BaseRepository 


class GuarantorRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, name: str, document_number: str) -> GuarantorModel:
        guarantor = GuarantorModel(name=name, document_number=document_number)
        self.db.add(guarantor)
        self.db.flush()
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
        self.db.flush()
        return guarantor_model

    def delete(self, guarantor_model: GuarantorModel) -> None:
        self.db.delete(guarantor_model)
        self.db.flush()