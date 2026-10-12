from pydantic import BaseModel

class PropertyCreateSchema(BaseModel):
    property_name: str
    owner_key: str
    address: str
    room_count: int

class PropertyUpdateSchema(BaseModel):
    property_name: str
    owner_key: str
    address: str
    room_count: int