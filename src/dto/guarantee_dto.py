from pydantic import BaseModel, ConfigDict
from typing import Optional

class DepositDTO(BaseModel):
    key: str
    type: str
    amount: float
    paid_in_cash: Optional[bool]
    deposit_date: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class GuarantorDTO(BaseModel):
    key: str
    type: str
    name: str
    document_number: str
    model_config = ConfigDict(from_attributes=True)

class BailInsuranceDTO(BaseModel):
    key: str
    type: str
    value: float
    validity: str
    insurance_company: str
    model_config = ConfigDict(from_attributes=True)