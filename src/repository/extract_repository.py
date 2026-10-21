from sqlalchemy.orm import Session, joinedload
from src.models import ExtractItemModel, ExtractModel
from src.repository.base_repository import BaseRepository
from src.repository.extract_batch_repository import ExtractBatchRepository

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

    def get_by_contract_ids(self, contract_ids: set[int]) -> list[ExtractModel]:
        if not contract_ids:
            return []
        return (
            self.db.query(ExtractModel)
            .filter(ExtractModel.contract_id.in_(contract_ids))
            .all()
        )

    def get_by_batch_id(self, batch_id: int) -> list[ExtractModel]:
        return (
            self.db.query(ExtractModel)
            .filter(ExtractModel.extract_batch_id == batch_id)
            .all()
        )

    def update(self, extract_model: ExtractModel, month_ref: int, year_ref: int, net_transfer: float, contract_id: int) -> ExtractModel:
        extract_model.month_ref = month_ref
        extract_model.year_ref = year_ref
        extract_model.net_transfer = net_transfer
        extract_model.contract_id = contract_id
        
        self.db.flush()
        return extract_model

    def delete(self, extract_model: ExtractModel) -> None:
        self.delete_many([extract_model])

    def delete_for_batch_update(self, extract_model: ExtractModel) -> None:
        self.db.delete(extract_model)
        self.db.flush()
        ExtractBatchRepository(self.db).unlink_by_id(extract_model.extract_batch_id)

    def delete_many(self, extracts: list[ExtractModel]) -> None:
        if not extracts:
            return

        extract_batch_repository = ExtractBatchRepository(self.db)
        batch_ids = {extract.extract_batch_id for extract in extracts}
        batches = extract_batch_repository.get_by_ids(batch_ids)
        for extract in extracts:
            self.db.delete(extract)
        self.db.flush()

        for batch in batches:
            remaining_extracts = self.get_by_batch_id(batch.id)
            extract_batch_repository.update_after_extract_deletion(
                batch,
                remaining_extracts,
            )