from pydantic import BaseModel, ConfigDict
from typing import Optional

from src.dto.property_dto import PropertyDTO
from src.dto.tenant_dto import TenantDTO
from src.dto.real_estate_dto import RealEstateDTO
from src.dto.guarantor_dto import GuarantorDTO
from src.dto.bail_insurance_dto import BailInsuranceDTO

class ContractDTO(BaseModel):
    key: str
    guarantee: str
    rental_deposit: float
    rent_amount: float
    room_name: Optional[str]
    acting: str
    file_path: Optional[str]
    
    property: PropertyDTO
    tenant: TenantDTO
    real_estate: Optional[RealEstateDTO] = None
    guarantor: Optional[GuarantorDTO] = None
    bail_insurance: Optional[BailInsuranceDTO] = None

    model_config = ConfigDict(from_attributes=True)