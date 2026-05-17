from pydantic import BaseModel, ConfigDict
from typing import Optional
from src.dto.contract_dto import ContractDTO

class ExtractDTO(BaseModel):
    key: str
    month_ref: int
    year_ref: int
    rent_amount: float
    receipt_path: Optional[str]
    iptu: float
    water: float
    agreement: float
    contract: ContractDTO

    model_config = ConfigDict(from_attributes=True)