from pydantic import BaseModel, ConfigDict
from src.dto.owner_dto import OwnerDTO

class PropertyDTO(BaseModel):
    key: str
    property_name: str
    owner: OwnerDTO
    address: str
    room_count: int

    model_config = ConfigDict(from_attributes=True)