from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.models import GuarantorModel, ContractModel, ContractStatusModel
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

    def get_paginated(
        self,
        skip: int = 0,
        limit: int = 10,
        search_term: str | None = None,
        name: str | None = None,
        document_number: str | None = None,
        only_active_contracts: bool = False
    ) -> tuple[int, list[GuarantorModel]]:
        
        query = self.db.query(GuarantorModel)

        if search_term:
            query = query.filter(
                or_(
                    GuarantorModel.name.ilike(f"%{search_term}%"),
                    GuarantorModel.document_number.ilike(f"%{search_term}%")
                )
            )

        if name:
            query = query.filter(GuarantorModel.name.ilike(f"%{name}%"))
            
        if document_number:
            query = query.filter(GuarantorModel.document_number.ilike(f"%{document_number}%"))

        if only_active_contracts:
            query = query.join(ContractModel, ContractModel.guarantor_id == GuarantorModel.id) \
                         .join(ContractStatusModel, ContractModel.status_id == ContractStatusModel.id) \
                         .filter(ContractStatusModel.enumerator == "active") \
                         .distinct()

        total_count = query.count()
        items = query.offset(skip).limit(limit).all()

        return total_count, items

    def update(self, guarantor_model: GuarantorModel, name: str, document_number: str) -> GuarantorModel:
        guarantor_model.name = name
        guarantor_model.document_number = document_number
        self.db.flush()
        return guarantor_model

    def delete(self, guarantor_model: GuarantorModel) -> None:
        self.db.delete(guarantor_model)
        self.db.flush()