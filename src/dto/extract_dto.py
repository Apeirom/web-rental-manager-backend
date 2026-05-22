from pydantic import BaseModel, ConfigDict
from typing import Optional
from src.dto.contract_dto import ContractDTO

class ExtractDTO(BaseModel):
    key: str
    month_ref: int
    year_ref: int
    
    rent_amount: float
    iptu: float
    water: float
    maintenance: float
    agreement: float
    penalty: float
    interest: float
    other_revenues: float
    
    administration_fee: float
    bank_fee: float
    net_transfer: float
    
    receipt_path: Optional[str]
    contract: ContractDTO

    model_config = ConfigDict(from_attributes=True)