from pydantic import BaseModel, ConfigDict

class PropertyDTO(BaseModel):
    key: str
    property_name: str
    owner_name: str
    address: str
    room_count: int

    model_config = ConfigDict(from_attributes=True)