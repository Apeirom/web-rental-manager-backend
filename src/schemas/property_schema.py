from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from src.constants.property_constants import EQUITY_PARTICIPATION_PERCENTAGE_BASE


class EquityParticipationSchema(BaseModel):
    owner_key: str
    participation_percentage: Decimal = Field(
        gt=0,
        le=EQUITY_PARTICIPATION_PERCENTAGE_BASE,
    )


class PropertySchema(BaseModel):
    property_name: str
    owner_key: str | None = None
    equity_participations: list[EquityParticipationSchema] | None = None
    address: str
    room_count: int

    @model_validator(mode="after")
    def validate_equity_participations(self):
        if self.owner_key and self.equity_participations:
            raise ValueError("Informe owner_key legado ou equity_participations, não ambos.")

        if not self.owner_key and not self.equity_participations:
            raise ValueError("Informe ao menos uma participação de proprietário.")

        if self.equity_participations:
            owner_keys = [item.owner_key for item in self.equity_participations]
            if len(owner_keys) != len(set(owner_keys)):
                raise ValueError("Um proprietário deve aparecer uma única vez por imóvel.")

            total_percentage = sum(
                (item.participation_percentage for item in self.equity_participations),
                Decimal("0"),
            )
            if total_percentage > EQUITY_PARTICIPATION_PERCENTAGE_BASE:
                raise ValueError("A soma das participações do imóvel não pode exceder 100%.")

        return self


class PropertyCreateSchema(PropertySchema):
    pass


class PropertyUpdateSchema(PropertySchema):
    pass
