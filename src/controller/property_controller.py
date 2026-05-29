from sqlalchemy.orm import Session
from src.repository.property_repository import PropertyRepository
from src.schemas.property_schema import PropertyCreateSchema, PropertyUpdateSchema
from src.dto.property_dto import PropertyDTO
from src.errors.custom_errors import PropertyNotFoundError

class PropertyController:
    def __init__(self, db: Session):
        self.property_repository = PropertyRepository(db)

    def create_property(self, schema: PropertyCreateSchema) -> PropertyDTO:
        property_model = self.property_repository.create(
            property_name=schema.property_name,
            owner_name=schema.owner_name,
            address=schema.address,
            room_count=schema.room_count
        )
        return PropertyDTO.model_validate(property_model)

    def get_property(self, property_key: str) -> PropertyDTO:
        property_model = self.property_repository.get_by_key(property_key)
        if not property_model:
            raise PropertyNotFoundError(property_key=property_key)
        return PropertyDTO.model_validate(property_model)

    def get_all_properties(self) -> list[PropertyDTO]:
        properties = self.property_repository.get_all()
        return [PropertyDTO.model_validate(p) for p in properties]

    def update_property(self, property_key: str, schema: PropertyUpdateSchema) -> PropertyDTO:
        property_model = self.property_repository.get_by_key(property_key)
        if not property_model:
            raise PropertyNotFoundError(property_key=property_key)
            
        updated_model = self.property_repository.update(
            property_model=property_model,
            property_name=schema.property_name,
            owner_name=schema.owner_name,
            address=schema.address,
            room_count=schema.room_count
        )
        return PropertyDTO.model_validate(updated_model)

    def delete_property(self, property_key: str) -> None:
        property_model = self.property_repository.get_by_key(property_key)
        if not property_model:
            raise PropertyNotFoundError(property_key=property_key)
        self.property_repository.delete(property_model)