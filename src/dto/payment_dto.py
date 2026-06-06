from pydantic import BaseModel, ConfigDict
from typing import Optional

class PaymentDTO(BaseModel):
    key: str
    payment_date: str
    amount: float
    
    status: str
    extract_key: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PaymentReconciliationDTO(BaseModel):
    status: str
    message: str
    candidates: Optional[list[PaymentDTO]] = None