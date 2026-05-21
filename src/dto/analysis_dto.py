from pydantic import BaseModel

class IncomeTaxRowDTO(BaseModel):
    reference_date: str
    tenant_name: str
    document: str
    document_type: str
    property_details: str
    rent_amount: float
    iptu: float
    water: float
    agreement: float
    commission_amount: float
    net_income: float