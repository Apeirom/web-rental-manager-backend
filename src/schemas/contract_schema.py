from pydantic import BaseModel
from typing import Optional

class ContractCreateSchema(BaseModel):
    guarantee_type: str
    rental_deposit: float
    rent_amount: float
    room_name: Optional[str] = None
    status: Optional[str] = "active"
    file_path: Optional[str] = None
    property_key: str
    tenant_key: str
    real_estate_key: Optional[str] = None
    guarantor_key: Optional[str] = None
    bail_insurance_key: Optional[str] = None

class ContractUpdateSchema(BaseModel):
    guarantee_type: str
    rental_deposit: float
    rent_amount: float
    room_name: Optional[str] = None
    status: Optional[str] = "active"
    file_path: Optional[str] = None
    property_key: str
    tenant_key: str
    real_estate_key: Optional[str] = None
    guarantor_key: Optional[str] = None
    bail_insurance_key: Optional[str] = None