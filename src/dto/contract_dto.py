from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional

from src.dto.property_dto import PropertyDTO
from src.dto.tenant_dto import TenantDTO
from src.dto.real_estate_dto import RealEstateDTO
from src.dto.guarantor_dto import GuarantorDTO
from src.dto.bail_insurance_dto import BailInsuranceDTO

class ContractDTO(BaseModel):
    key: str
    rental_deposit: float
    rent_amount: float
    room_name: Optional[str]
    file_path: Optional[str]
    
    guarantee_type: str
    status: str

    property: PropertyDTO
    tenant: TenantDTO
    real_estate: Optional[RealEstateDTO] = None
    guarantor: Optional[GuarantorDTO] = None
    bail_insurance: Optional[BailInsuranceDTO] = None

    @field_validator('status', 'guarantee_type', mode='before')
    @classmethod
    def extract_enumerator(cls, value) -> str:
        if hasattr(value, 'enumerator'):
            return value.enumerator
        
        return value



    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    model_config = ConfigDict(from_attributes=True)