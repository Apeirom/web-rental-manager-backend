from fastapi import APIRouter

from src.routers.reports.income_tax_router import income_tax_router

reports_router = APIRouter(prefix="/reports")
reports_router.include_router(income_tax_router)
