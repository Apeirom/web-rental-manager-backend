from pydantic import BaseModel, ConfigDict
from src.dto.owner_dto import OwnerDTO

class EquityParticipationDTO(BaseModel):
    owner: OwnerDTO
    participation_percentage: float

    model_config = ConfigDict(from_attributes=True)

class PropertyDTO(BaseModel):
    key: str
    property_name: str
    equity_participations: list[EquityParticipationDTO]
    address: str
    room_count: int

    model_config = ConfigDict(from_attributes=True)