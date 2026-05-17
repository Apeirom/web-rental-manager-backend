from pydantic import BaseModel, ConfigDict

class BailInsuranceDTO(BaseModel):
    key: str
    value: float
    validity: str
    insurance_company: str

    model_config = ConfigDict(from_attributes=True)