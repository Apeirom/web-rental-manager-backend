from pydantic import BaseModel
from typing import Optional

class ContractSchema(BaseModel):
    rent_amount: float
    room_name: Optional[str] = None
    status: Optional[str] = "active"
    file_path: Optional[str] = None
    
    property_key: str
    tenant_key: str
    real_estate_key: Optional[str] = None
    
    guarantee_key: Optional[str] = None