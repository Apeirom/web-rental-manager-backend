from pydantic import BaseModel
from typing import Optional

class PaymentCreateSchema(BaseModel):
    payment_date: str
    amount: float

class PaymentUpdateSchema(BaseModel):
    payment_date: str
    amount: float
    extract_key: Optional[str] = None