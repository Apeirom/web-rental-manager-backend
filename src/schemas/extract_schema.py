from typing import Optional, List
from pydantic import BaseModel
from src.schemas.extract_item_schema import ExtractItemCreateSchema, ExtractItemUpdateSchema

class ExtractCreateSchema(BaseModel):
    contract_key: str
    month_ref: int
    year_ref: int
    
    items: List[ExtractItemCreateSchema]

class ExtractUpdateSchema(BaseModel):
    key: Optional[str] = None
    contract_key: str
    month_ref: int
    year_ref: int
    
    items: List[ExtractItemUpdateSchema]