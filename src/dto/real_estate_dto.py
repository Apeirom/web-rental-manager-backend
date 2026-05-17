from pydantic import BaseModel, ConfigDict

class RealEstateDTO(BaseModel):
    key: str
    name: str
    cnpj: str
    address: str
    commission: float
    phone: str

    model_config = ConfigDict(from_attributes=True)