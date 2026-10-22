from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer
from datetime import date

from src.controller.income_tax_controller import IncomeTaxController
from src.dependencies.income_tax import get_income_tax_controller
from src.dto.income_tax_dto import IncomeTaxSummaryDTO

bearer_scheme = HTTPBearer()

income_tax_router = APIRouter(
    prefix="/income-tax",
    tags=["Relatórios - Carnê-Leão"],
    dependencies=[Depends(bearer_scheme)],
)


@income_tax_router.get("/summary", response_model=IncomeTaxSummaryDTO)
def get_income_tax_summary(
    owner_key: str | None = None,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    controller: IncomeTaxController = Depends(get_income_tax_controller),
) -> IncomeTaxSummaryDTO:
    return controller.get_summary(
        owner_key=owner_key,
        start_date=start_date,
        end_date=end_date,
    )


@income_tax_router.get("/export")
def export_income_tax_csv(
    owner_key: str | None = None,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    controller: IncomeTaxController = Depends(get_income_tax_controller),
) -> StreamingResponse:
    content, summary = controller.export_csv(
        owner_key=owner_key,
        start_date=start_date,
        end_date=end_date,
    )
    start = summary.start_date or "inicio"
    filename = f"carne-leao-{start}-ate-{summary.end_date}.csv"
    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
