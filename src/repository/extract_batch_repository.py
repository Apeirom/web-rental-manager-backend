from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import or_
from src.models import (
    ContractModel,
    ContractStatusModel,
    EquityParticipationModel,
    ExtractBatchModel,
    ExtractModel,
    PropertyModel,
    TenantModel,
)
from src.repository.base_repository import BaseRepository 

class ExtractBatchRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, total_net_transfer: float, file_path: str | None = None) -> ExtractBatchModel:
        batch = ExtractBatchModel(
            total_net_transfer=total_net_transfer,
            file_path=file_path
        )
        self.db.add(batch)
        self.db.flush()
        return batch

    def get_by_key(self, batch_key: str) -> ExtractBatchModel | None:
        return self.db.query(ExtractBatchModel).filter(ExtractBatchModel.key == batch_key).first()

    def get_by_ids(self, batch_ids: set[int]) -> list[ExtractBatchModel]:
        if not batch_ids:
            return []
        return (
            self.db.query(ExtractBatchModel)
            .filter(ExtractBatchModel.id.in_(batch_ids))
            .all()
        )

    def unlink_payment(self, batch_model: ExtractBatchModel) -> None:
        batch_model.payment_id = None
        self.db.flush()

    def unlink_by_id(self, batch_id: int) -> None:
        batch = self.db.query(ExtractBatchModel).filter(
            ExtractBatchModel.id == batch_id
        ).first()
        if batch is not None:
            self.unlink_payment(batch)

    def update_total(self, batch_model: ExtractBatchModel, new_total: float) -> None:
        if batch_model.total_net_transfer != new_total:
            batch_model.payment_id = None
            
        batch_model.total_net_transfer = new_total
        self.db.flush()

    def update_after_extract_deletion(
        self,
        batch_model: ExtractBatchModel,
        remaining_extracts: list[ExtractModel],
    ) -> None:
        batch_model.payment_id = None
        if remaining_extracts:
            batch_model.total_net_transfer = round(
                sum(extract.net_transfer for extract in remaining_extracts),
                2,
            )
        else:
            self.db.delete(batch_model)
        self.db.flush()

    def get_paginated(
        self,
        skip: int = 0,
        limit: int = 10,
        search_term: str | None = None,
        only_active_contracts: bool = False,
        is_reconciled: bool | None = None
    ) -> tuple[int, list[ExtractBatchModel]]:
        
        query = self.db.query(ExtractBatchModel).options(
            selectinload(ExtractBatchModel.extracts)
            .joinedload(ExtractModel.contract)
            .joinedload(ContractModel.property)
            .selectinload(PropertyModel.equity_participations)
            .joinedload(EquityParticipationModel.owner)
        )

        if search_term or only_active_contracts:
            query = query.join(ExtractBatchModel.extracts).join(ExtractModel.contract)

            if search_term:
                query = query.join(ContractModel.property).join(ContractModel.tenant).filter(
                    or_(
                        PropertyModel.property_name.ilike(f"%{search_term}%"),
                        TenantModel.name.ilike(f"%{search_term}%"),
                        ContractModel.room_name.ilike(f"%{search_term}%")
                    )
                )

            if only_active_contracts:
                query = query.join(ContractStatusModel, ContractModel.status_id == ContractStatusModel.id).filter(
                    ContractStatusModel.enumerator == "active"
                )

        if is_reconciled is True:
            query = query.filter(ExtractBatchModel.payment_id.isnot(None))
        elif is_reconciled is False:
            query = query.filter(ExtractBatchModel.payment_id.is_(None))

        query = query.distinct()

        total_count = query.count()
        items = query.offset(skip).limit(limit).all()

        return total_count, items

    def delete(self, batch_model: ExtractBatchModel) -> None:
        batch_model.payment_id = None
        self.db.delete(batch_model)
        self.db.flush()