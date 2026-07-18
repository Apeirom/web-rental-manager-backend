from pydantic import BaseModel

class ExtractCreateSchema(BaseModel):
    contract_key: str
    month_ref: int
    year_ref: int
    
    rent_amount: float = 0.0
    iptu: float = 0.0
    water: float = 0.0
    maintenance: float = 0.0
    agreement: float = 0.0
    penalty: float = 0.0
    interest: float = 0.0
    other_revenues: float = 0.0
    bank_fee: float = 0.0

class ExtractUpdateSchema(ExtractCreateSchema):
    key: str
    
