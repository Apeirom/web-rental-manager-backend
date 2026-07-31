from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Union

from src.dto.property_dto import PropertyDTO
from src.dto.tenant_dto import TenantDTO
from src.dto.real_estate_dto import RealEstateDTO
from src.dto.guarantee_dto import BailInsuranceDTO, DepositDTO, GuarantorDTO
from src.dto.base_enumerator_dto import EnumeratorString

class ContractDTO(BaseModel):
    key: str
    rent_amount: float
    room_name: Optional[str]
    file_path: Optional[str]
    status: EnumeratorString

    property: PropertyDTO
    tenant: TenantDTO
    real_estate: Optional[RealEstateDTO] = None
    
    guarantee: Optional[Union[DepositDTO, GuarantorDTO, BailInsuranceDTO]] = None

    model_config = ConfigDict(from_attributes=True)