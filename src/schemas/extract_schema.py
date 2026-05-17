from pydantic import BaseModel
from typing import Optional

class ExtractCreateSchema(BaseModel):
    month_ref: int
    year_ref: int
    rent_amount: float = 0.0
    receipt_path: Optional[str] = None
    iptu: float = 0.0
    water: float = 0.0
    agreement: float = 0.0
    contract_key: str

class ExtractUpdateSchema(BaseModel):
    month_ref: int
    year_ref: int
    rent_amount: float = 0.0
    receipt_path: Optional[str] = None
    iptu: float = 0.0
    water: float = 0.0
    agreement: float = 0.0
    contract_key: str