from pydantic import BaseModel, Field
from typing import Optional, Union, Literal
from typing_extensions import Annotated

class DepositSchema(BaseModel):
    type: Literal["deposit"]
    amount: float
    paid_in_cash: Optional[bool] = None
    deposit_date: Optional[str] = None

class GuarantorSchema(BaseModel):
    type: Literal["guarantor"]
    name: str
    document_number: str = Field(
        pattern=r"^(\d{2,3}(\.\d{3}){2}\/\d{4}-\d{2}|\d{3}(\.\d{3}){2}-\d{2})$"
    )

class BailInsuranceSchema(BaseModel):
    type: Literal["bail_insurance"]
    value: float
    validity: str
    insurance_company: str

GuaranteeSchema = Annotated[
    Union[DepositSchema, GuarantorSchema, BailInsuranceSchema],
    Field(discriminator="type")
]