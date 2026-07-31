from sqlalchemy.orm import Session
from src.models import ExtractItemModel
from src.repository.base_repository import BaseRepository

class ExtractItemRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, extract_id: int, category_id: int, description: str, amount: float, is_credit: bool, is_withheld_at_source: bool) -> ExtractItemModel:
        item = ExtractItemModel(
            extract_id=extract_id,
            category_id=category_id,
            description=description,
            amount=amount,
            is_credit=is_credit,
            is_withheld_at_source=is_withheld_at_source
        )
        self.db.add(item)
        self.db.flush()
        return item

    def get_by_key(self, item_key: str) -> ExtractItemModel | None:
        return self.db.query(ExtractItemModel).filter(ExtractItemModel.key == item_key).first()

    def update(self, item_model: ExtractItemModel, category_id: int, description: str, amount: float, is_credit: bool, is_withheld_at_source: bool) -> ExtractItemModel:
        item_model.category_id = category_id
        item_model.description = description
        item_model.amount = amount
        item_model.is_credit = is_credit
        item_model.is_withheld_at_source = is_withheld_at_source
        
        self.db.flush()
        return item_model

    def delete(self, item_model: ExtractItemModel) -> None:
        self.db.delete(item_model)
        self.db.flush()