from pydantic import BaseModel
from typing import Optional

class PaymentCreateSchema(BaseModel):
    payment_date: str
    amount: float

class PaymentUpdateSchema(BaseModel):
    payment_date: str
    amount: float
    status_enumerator: Optional[str] = None
    extract_key: Optional[str] = None