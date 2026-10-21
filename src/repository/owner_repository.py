from sqlalchemy import or_
from sqlalchemy.orm import Session
from src.models.owner_model import OwnerModel
from src.repository.base_repository import BaseRepository 
from src.repository.property_repository import PropertyRepository

class OwnerRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

   
    def get_by_key(self, owner_key: str) -> OwnerModel | None:
        return self.db.query(OwnerModel).filter(OwnerModel.key == owner_key).first()

    def get_paginated(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search_term: str | None = None
    ) -> tuple[int, list[OwnerModel]]:
        
        query = self.db.query(OwnerModel)

        if search_term:
            query = query.filter(
                or_(
                    OwnerModel.name.ilike(f"%{search_term}%"),
                    OwnerModel.document_number.ilike(f"%{search_term}%")
                )
            )

        total_count = query.count()
        items = query.offset(skip).limit(limit).all()

        return total_count, items
    
    def create(self, name: str, document_number: str | None = None) -> OwnerModel:
        new_owner = OwnerModel(
            name=name,
            document_number=document_number
        )
        self.db.add(new_owner)
        self.db.flush()
        return new_owner


    def update(self, owner_model: OwnerModel, name: str, document_number: str | None = None) -> OwnerModel:
        owner_model.name = name
        owner_model.document_number = document_number
        
        self.db.flush()
        return owner_model


    def delete(self, owner_model: OwnerModel) -> None:
        property_repository = PropertyRepository(self.db)
        properties = property_repository.get_by_owner_id(owner_model.id)
        exclusively_owned = [
            property_model
            for property_model in properties
            if len(property_model.equity_participations) == 1
        ]
        property_repository.delete_many(exclusively_owned)
        self.db.delete(owner_model)
        self.db.flush()