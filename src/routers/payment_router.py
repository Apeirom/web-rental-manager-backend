from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from src.database.config import get_db
from typing import Optional

from src.dto.paginated_response import PaginatedResponseDTO
from src.dto.payment_dto import PaymentDTO
from src.schemas.payment_schema import PaymentCreateSchema, PaymentUpdateSchema
from src.controller.payment_controller import PaymentController

bearer_scheme = HTTPBearer()

payment_router = APIRouter(
    prefix="/payments",
    tags=["8. Pagamentos (Payments)"],
    dependencies=[Depends(bearer_scheme)]
)

@payment_router.post("", response_model=PaymentDTO, status_code=status.HTTP_201_CREATED)
def create_payment(schema: PaymentCreateSchema, db: Session = Depends(get_db)):
    controller = PaymentController(db)
    return controller.create_payment(schema)

@payment_router.get("/{payment_key}", response_model=PaymentDTO)
def get_payment(payment_key: str, db: Session = Depends(get_db)):
    controller = PaymentController(db)
    return controller.get_payment(payment_key)

@payment_router.put("/{payment_key}", response_model=PaymentDTO)
def update_payment(payment_key: str, schema: PaymentUpdateSchema, db: Session = Depends(get_db)):
    controller = PaymentController(db)
    return controller.update_payment(payment_key, schema)

@payment_router.delete("/{payment_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_key: str, db: Session = Depends(get_db)):
    controller = PaymentController(db)
    controller.delete_payment(payment_key)

@payment_router.get("", response_model=PaginatedResponseDTO[PaymentDTO], response_model_exclude_none=True)
def list_payments(
    skip: int = 0, 
    limit: int = 10, 
    amount: Optional[float] = None,          
    start_date: Optional[str] = None,      
    end_date: Optional[str] = None,
    is_linked: Optional[bool] = None,            
    db: Session = Depends(get_db)
):
    controller = PaymentController(db)
    return controller.get_paginated_payments(skip, limit, amount, start_date, end_date, is_linked)
