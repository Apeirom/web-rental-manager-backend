from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Union

from src.dto.property_dto import PropertyDTO
from src.dto.tenant_dto import TenantDTO
from src.dto.real_estate_dto import RealEstateDTO
from src.dto.guarantee_dto import BailInsuranceDTO, DepositDTO, GuarantorDTO

class ContractDTO(BaseModel):
    key: str
    rent_amount: float
    room_name: Optional[str]
    file_path: Optional[str]
    status: str

    property: PropertyDTO
    tenant: TenantDTO
    real_estate: Optional[RealEstateDTO] = None
    
    guarantee: Optional[Union[DepositDTO, GuarantorDTO, BailInsuranceDTO]] = None

    @field_validator('status', mode='before')
    @classmethod
    def extract_enumerator(cls, value):
        if hasattr(value, 'enumerator'):
            return value.enumerator
        return value

    model_config = ConfigDict(from_attributes=True)