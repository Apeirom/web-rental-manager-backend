from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from src.dto.contract_dto import ContractDTO
from src.dto.extract_item_dto import ExtractItemDTO

class ExtractDTO(BaseModel):
    key: str
    month_ref: int
    year_ref: int
    net_transfer: float
    
    contract: ContractDTO
    
    items: List[ExtractItemDTO] = []

    model_config = ConfigDict(from_attributes=True)