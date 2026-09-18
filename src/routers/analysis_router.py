from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from src.database.config import get_db
from typing import Optional

from src.dto.analysis_dto import IncomeTaxRowDTO
from src.controller.analysis_controller import AnalysisController

bearer_scheme = HTTPBearer()


analysis_router = APIRouter(
    prefix="/analyses",
    tags=["10. Análises (Analyses)"],
    dependencies=[Depends(bearer_scheme)]
)

@analysis_router.get("/income-tax", response_model=list[IncomeTaxRowDTO])
def get_income_tax(
    start_year: int, 
    start_month: int, 
    end_year: int, 
    end_month: int, 
    owner_id: Optional[int] = Query(None),
    tax_rate: Optional[float] = Query(27.5),
    db: Session = Depends(get_db)
):
    controller = AnalysisController(db)
    return controller.generate_income_tax_report(
        start_year=start_year, 
        start_month=start_month, 
        end_year=end_year, 
        end_month=end_month,
        owner_id=owner_id,
        tax_rate=tax_rate
    )