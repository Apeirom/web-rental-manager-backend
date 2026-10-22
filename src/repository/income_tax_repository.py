from datetime import date, timedelta

from sqlalchemy.orm import Session, joinedload, selectinload

from src.models import (
    ContractModel,
    EquityParticipationModel,
    ExtractBatchModel,
    ExtractItemModel,
    ExtractModel,
    PaymentModel,
    PropertyModel,
)


class IncomeTaxRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_paid_extracts_for_period(
        self,
        start_date: date | None,
        end_date: date,
        owner_id: int | None,
    ) -> list[tuple[ExtractModel, EquityParticipationModel]]:
        query = (
            self.db.query(
                ExtractModel,
                EquityParticipationModel,
            )
            .join(ContractModel, ExtractModel.contract_id == ContractModel.id)
            .join(PropertyModel, ContractModel.property_id == PropertyModel.id)
            .join(
                EquityParticipationModel,
                EquityParticipationModel.property_id == PropertyModel.id,
            )
            .join(ExtractBatchModel, ExtractModel.extract_batch_id == ExtractBatchModel.id)
            .join(PaymentModel, ExtractBatchModel.payment_id == PaymentModel.id)
            .options(
                joinedload(EquityParticipationModel.owner),
                joinedload(ExtractModel.contract).joinedload(ContractModel.tenant),
                joinedload(ExtractModel.contract).joinedload(ContractModel.property),
                selectinload(ExtractModel.items).joinedload(
                    ExtractItemModel.category
                ),
                joinedload(ExtractModel.batch).joinedload(ExtractBatchModel.payment),
            )
            .filter(PaymentModel.payment_date < (end_date + timedelta(days=1)).isoformat())
        )
        if start_date is not None:
            query = query.filter(PaymentModel.payment_date >= start_date.isoformat())
        if owner_id is not None:
            query = query.filter(EquityParticipationModel.owner_id == owner_id)

        return query.order_by(
            PaymentModel.payment_date.asc(),
            ExtractModel.id.asc(),
            EquityParticipationModel.owner_id.asc(),
        ).all()
