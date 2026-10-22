from pydantic import BaseModel


class IncomeTaxItemDTO(BaseModel):
    key: str
    category: str
    description: str
    amount: float


class IncomeTaxExtractDTO(BaseModel):
    extract_key: str
    owner_key: str
    owner_name: str
    reference_date: str
    payment_date: str
    tenant_name: str
    tenant_document_number: str
    tenant_document_type: str
    property_name: str
    participation_percentage: float
    rent: float
    interest: float
    penalty: float
    administration_fee: float
    iptu: float
    total_income: float
    total_deductions: float
    taxable_base: float
    income_items: list[IncomeTaxItemDTO]
    deduction_items: list[IncomeTaxItemDTO]


class IncomeTaxSummaryDTO(BaseModel):
    owner_key: str | None
    owner_name: str | None
    start_date: str | None
    end_date: str
    total_income: float
    total_deductions: float
    taxable_base: float
    extracts: list[IncomeTaxExtractDTO]
