from pydantic import BaseModel
from typing import Optional

class ExtractBaseSchema(BaseModel):
    month_ref: int
    year_ref: int
    receipt_path: Optional[str] = None

    rent_amount: float = 0.0
    iptu: float = 0.0
    water: float = 0.0
    maintenance: float = 0.0
    agreement: float = 0.0
    penalty: float = 0.0
    interest: float = 0.0
    other_revenues: float = 0.0
    bank_fee: float = 0.0

class ExtractCreateSchema(ExtractBaseSchema):
    contract_key: str

class ExtractUpdateSchema(ExtractBaseSchema):
    contract_key: str