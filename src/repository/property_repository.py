from sqlalchemy.orm import Session
from src.models.property_model import PropertyModel
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

    def get_all(self) -> list[PropertyModel]:
        return self.db.query(PropertyModel).all()

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