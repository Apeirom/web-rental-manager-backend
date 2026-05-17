from pydantic import BaseModel

class BailInsuranceCreateSchema(BaseModel):
    value: float
    validity: str
    insurance_company: str

class BailInsuranceUpdateSchema(BaseModel):
    value: float
    validity: str
    insurance_company: str