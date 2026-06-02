from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.models import PropertyModel, ContractModel, ContractStatusModel
from src.repository.base_repository import BaseRepository 


class PropertyRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, property_name: str, owner_name: str, address: str, room_count: int) -> PropertyModel:
        new_property = PropertyModel(
            property_name=property_name,
            owner_name=owner_name,
            address=address,
            room_count=room_count
        )
        self.db.add(new_property)
        self.db.flush()
        return new_property

    def get_by_key(self, property_key: str) -> PropertyModel | None:
        return self.db.query(PropertyModel).filter(PropertyModel.key == property_key).first()

    def get_paginated(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search_term: str | None = None,
        property_name: str | None = None,
        owner_name: str | None = None,
        only_active_contracts: bool = False
    ) -> tuple[int, list[PropertyModel]]:
        
        query = self.db.query(PropertyModel)

        if search_term:
            query = query.filter(
                or_(
                    PropertyModel.property_name.ilike(f"%{search_term}%"),
                    PropertyModel.owner_name.ilike(f"%{search_term}%")
                )
            )

        if property_name:
            query = query.filter(PropertyModel.property_name.ilike(f"%{property_name}%"))
        if owner_name:
            query = query.filter(PropertyModel.owner_name.ilike(f"%{owner_name}%"))

        if only_active_contracts:
            query = query.join(ContractModel, ContractModel.property_id == PropertyModel.id) \
                         .join(ContractStatusModel, ContractModel.status_id == ContractStatusModel.id) \
                         .filter(ContractStatusModel.enumerator == "active") \
                         .distinct()

        total_count = query.count()
        items = query.offset(skip).limit(limit).all()

        return total_count, items

    def update(self, property_model: PropertyModel, property_name: str, owner_name: str, address: str, room_count: int) -> PropertyModel:
        property_model.property_name = property_name
        property_model.owner_name = owner_name
        property_model.address = address
        property_model.room_count = room_count
        self.db.flush()
        return property_model

    def delete(self, property_model: PropertyModel) -> None:
        self.db.delete(property_model)
        self.db.flush()