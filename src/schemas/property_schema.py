from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class EquityParticipationSchema(BaseModel):
    owner_key: str
    participation_percentage: Decimal


class PropertySchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    property_name: str
    equity_participations: list[EquityParticipationSchema] = Field(
        default_factory=list
    )
    address: str
    room_count: int


class PropertyCreateSchema(PropertySchema):
    pass


class PropertyUpdateSchema(PropertySchema):
    pass
