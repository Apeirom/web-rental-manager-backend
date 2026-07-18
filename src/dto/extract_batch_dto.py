# src/dto/extract_dto.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from src.dto.extract_dto import ExtractDTO
from src.dto.payment_dto import PaymentDTO

class ExtractBatchDTO(BaseModel):
    key: str
    total_net_transfer: float
    file_path: Optional[str]
    status: str
    extracts: List[ExtractDTO]
    
    payment: Optional['PaymentDTO'] = None 

    model_config = ConfigDict(from_attributes=True)