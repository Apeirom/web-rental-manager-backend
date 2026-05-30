from pydantic import BaseModel
from typing import Optional

class PaymentCreateSchema(BaseModel):
    payment_date: str
    month_ref: int
    year_ref: int
    file_path: Optional[str] = None
    contract_key: str

class PaymentUpdateSchema(BaseModel):
    payment_date: str
    month_ref: int
    year_ref: int
    file_path: Optional[str] = None
    contract_key: str