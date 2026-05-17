from pydantic import BaseModel, ConfigDict
from typing import Optional
from src.dto.contract_dto import ContractDTO

class PaymentDTO(BaseModel):
    key: str
    payment_date: str
    month_ref: int
    year_ref: int
    receipt_path: Optional[str]
    contract: ContractDTO

    model_config = ConfigDict(from_attributes=True)