from sqlalchemy.orm import Session, joinedload
from typing import Optional
from src.models import ExtractModel, ContractModel, ExtractItemModel, PropertyModel
from src.repository.base_repository import BaseRepository

class ExtractRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, month_ref: int, year_ref: int, net_transfer: float, contract_id: int, extract_batch_id: int) -> ExtractModel:
        extract = ExtractModel(
            month_ref=month_ref,
            year_ref=year_ref,
            net_transfer=net_transfer,
            contract_id=contract_id,
            extract_batch_id=extract_batch_id
        )
        self.db.add(extract)
        self.db.flush()
        return extract

    def get_by_key(self, extract_key: str) -> ExtractModel | None:
        return self.db.query(ExtractModel).options(
            joinedload(ExtractModel.items).joinedload(ExtractItemModel.category)
        ).filter(ExtractModel.key == extract_key).first()

    def get_by_date_range_with_relations(
        self, 
        start_year: int, 
        start_month: int, 
        end_year: int, 
        end_month: int,
        owner_id: Optional[int] = None
    ):
        start_val = (start_year * 12) + start_month
        end_val = (end_year * 12) + end_month

        query = self.db.query(ExtractModel).options(
            joinedload(ExtractModel.contract).joinedload(ContractModel.tenant),
            joinedload(ExtractModel.contract).joinedload(ContractModel.property),
            joinedload(ExtractModel.contract).joinedload(ContractModel.real_estate),
            joinedload(ExtractModel.items).joinedload(ExtractItemModel.category)
        )

        if owner_id is not None:
            query = query.join(ContractModel, ExtractModel.contract_id == ContractModel.id) \
                         .join(PropertyModel, ContractModel.property_id == PropertyModel.id) \
                         .filter(PropertyModel.owner_id == owner_id)

        return query.filter(
            ((ExtractModel.year_ref * 12) + ExtractModel.month_ref) >= start_val,
            ((ExtractModel.year_ref * 12) + ExtractModel.month_ref) <= end_val
        ).order_by(ExtractModel.year_ref.asc(), ExtractModel.month_ref.asc()).all()

    def update(self, extract_model: ExtractModel, month_ref: int, year_ref: int, net_transfer: float, contract_id: int) -> ExtractModel:
        extract_model.month_ref = month_ref
        extract_model.year_ref = year_ref
        extract_model.net_transfer = net_transfer
        extract_model.contract_id = contract_id
        
        self.db.flush()
        return extract_model

    def delete(self, extract_model: ExtractModel) -> None:
        self.db.delete(extract_model)
        self.db.flush()