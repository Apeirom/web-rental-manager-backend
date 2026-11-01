from decimal import Decimal

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from src.models import (
    ContractModel,
    ContractStatusModel,
    EquityParticipationModel,
    PropertyModel,
)
from src.models.owner_model import OwnerModel
from src.repository.base_repository import BaseRepository
from src.repository.contract_repository import ContractRepository


class PropertyRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(
        self,
        property_name: str,
        participations: list[tuple[int, Decimal]],
        address: str,
        room_count: int,
    ) -> PropertyModel:
        new_property = PropertyModel(
            property_name=property_name,
            address=address,
            room_count=room_count,
        )
        self.db.add(new_property)
        self.db.flush()
        new_property.equity_participations = [
            EquityParticipationModel(
                owner_id=owner_id,
                participation_percentage=percentage,
            )
            for owner_id, percentage in participations
        ]
        self.db.flush()
        return new_property

    def get_by_key(
        self, property_key: str, for_update: bool = False
    ) -> PropertyModel | None:
        query = self.db.query(PropertyModel).options(
            selectinload(PropertyModel.equity_participations).joinedload(
                EquityParticipationModel.owner
            )
        )
        if for_update:
            query = query.with_for_update()
        return query.filter(PropertyModel.key == property_key).first()

    def get_by_owner_id(self, owner_id: int) -> list[PropertyModel]:
        return (
            self.db.query(PropertyModel)
            .join(PropertyModel.equity_participations)
            .filter(EquityParticipationModel.owner_id == owner_id)
            .options(
                selectinload(PropertyModel.equity_participations).joinedload(
                    EquityParticipationModel.owner
                )
            )
            .all()
        )

    def get_paginated(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search_term: str | None = None,
        property_name: str | None = None,
        owner_name: str | None = None,
        only_active_contracts: bool = False
    ) -> tuple[int, list[PropertyModel]]:
        
        query = self.db.query(PropertyModel).options(
            selectinload(PropertyModel.equity_participations).joinedload(
                EquityParticipationModel.owner
            )
        )

        if search_term or owner_name:
            query = query.join(PropertyModel.equity_participations).join(
                EquityParticipationModel.owner
            )

        if search_term:
            query = query.filter(
                or_(
                    PropertyModel.property_name.ilike(f"%{search_term}%"),
                    OwnerModel.name.ilike(f"%{search_term}%")
                )
            )

        if property_name:
            query = query.filter(PropertyModel.property_name.ilike(f"%{property_name}%"))
            
        if owner_name:
            query = query.filter(OwnerModel.name.ilike(f"%{owner_name}%"))

        if only_active_contracts:
            query = query.join(ContractModel, ContractModel.property_id == PropertyModel.id) \
                         .join(ContractStatusModel, ContractModel.status_id == ContractStatusModel.id) \
                         .filter(ContractStatusModel.enumerator == "active") \
                         .distinct()

        if search_term or owner_name:
            query = query.distinct()

        total_count = query.count()
        items = query.offset(skip).limit(limit).all()

        return total_count, items

    def update(
        self,
        property_model: PropertyModel,
        property_name: str,
        participations: list[tuple[int, Decimal]],
        address: str,
        room_count: int,
    ) -> PropertyModel:
        property_model.property_name = property_name
        property_model.address = address
        property_model.room_count = room_count
        property_model.equity_participations.clear()
        self.db.flush()
        property_model.equity_participations = [
            EquityParticipationModel(
                owner_id=owner_id,
                participation_percentage=percentage,
            )
            for owner_id, percentage in participations
        ]
        self.db.flush()
        return property_model

    def delete(self, property_model: PropertyModel) -> None:
        self.delete_many([property_model])

    def delete_many(self, properties: list[PropertyModel]) -> None:
        if not properties:
            return

        contract_repository = ContractRepository(self.db)
        property_ids = {property_model.id for property_model in properties}
        contracts = contract_repository.get_by_property_ids(property_ids)
        contract_repository.delete_many(contracts)

        for property_model in properties:
            self.db.delete(property_model)
        self.db.flush()