from pydantic import BaseModel
from typing import List, Optional

class ExtractItemDTO(BaseModel):
    category: str
    amount: float
    type: str

class IncomeTaxRowDTO(BaseModel):
    reference_date: str
    tenant_name: str
    tenat_document_number: str
    tenat_document_type: str
    property_details: str

    total_credits: float
    total_debits: float
    tax_rate_used: float
    calculated_tax: float
    
    items: List[ExtractItemDTO]