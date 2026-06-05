from pydantic import BaseModel, ConfigDict, computed_field, field_validator
from typing import Optional, List

class PaymentDTO(BaseModel):
    key: str
    payment_date: str
    amount: float
    status: str
    
    @field_validator('status', mode='before')
    @classmethod
    def extract_status(cls, v):
        if hasattr(v, 'enumerator'):
            return v.enumerator
        return v
    
    @computed_field
    def extract_key(self) -> Optional[str]:
        return self.extract.key if hasattr(self, 'extract') and self.extract else None

    model_config = ConfigDict(from_attributes=True)

class PaymentReconciliationDTO(BaseModel):
    status: str
    message: str
    candidates: Optional[List[PaymentDTO]] = None