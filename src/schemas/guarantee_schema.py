from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, Literal
from typing_extensions import Annotated

from src.utils.document_number import normalize_document_number

class DepositSchema(BaseModel):
    type: Literal["deposit"]
    amount: float
    paid_in_cash: Optional[bool] = None
    deposit_date: Optional[str] = None

class GuarantorSchema(BaseModel):
    type: Literal["guarantor"]
    name: str
    document_number: str

    @field_validator("document_number")
    @classmethod
    def validate_document_number(cls, value):
        return normalize_document_number(value)

class BailInsuranceSchema(BaseModel):
    type: Literal["bail_insurance"]
    value: float
    validity: str
    insurance_company: str

GuaranteeSchema = Annotated[
    Union[DepositSchema, GuarantorSchema, BailInsuranceSchema],
    Field(discriminator="type")
]