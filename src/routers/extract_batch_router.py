from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from src.database.config import get_db
from typing import Optional

from src.dto.paginated_response import PaginatedResponseDTO
from src.dto.payment_dto import PaymentReconciliationDTO
from src.dto.extract_batch_dto import ExtractBatchDTO
from src.dto.extract_dto import ExtractDTO
from src.schemas.extract_batch_schema import ExtractBatchCreateSchema, ExtractBatchUpdateSchema
from src.controller.extract_batch_controller import ExtractBatchController
from src.controller.extract_controller import ExtractController

bearer_scheme = HTTPBearer()


extract_batch_router = APIRouter(
    prefix="/extract-batches",
    tags=["9. Lotes de Extratos (Extract Batches)"],
    dependencies=[Depends(bearer_scheme)]
)

@extract_batch_router.post("", response_model=ExtractBatchDTO, status_code=status.HTTP_201_CREATED)
def create_extract_batch(schema: ExtractBatchCreateSchema, db: Session = Depends(get_db)):
    controller = ExtractBatchController(db)
    return controller.create_batch(schema)

@extract_batch_router.get("/{batch_key}", response_model=ExtractBatchDTO)
def get_extract_batch(batch_key: str, db: Session = Depends(get_db)):
    controller = ExtractBatchController(db)
    return controller.get_batch(batch_key)

@extract_batch_router.get("", response_model=PaginatedResponseDTO[ExtractBatchDTO])
def list_extract_batches(
    skip: int = 0, 
    limit: int = 10, 
    search_term: Optional[str] = None,
    only_active_contracts: bool = False,
    is_reconciled: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    controller = ExtractBatchController(db)
    return controller.get_paginated_batches(skip, limit, search_term, only_active_contracts, is_reconciled)

@extract_batch_router.put("/{batch_key}", response_model=ExtractBatchDTO)
def update_extract_batch(batch_key: str, schema: ExtractBatchUpdateSchema, db: Session = Depends(get_db)):
    controller = ExtractBatchController(db)
    return controller.update_batch(batch_key, schema)

@extract_batch_router.delete("/{batch_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_extract_batch(batch_key: str, db: Session = Depends(get_db)):
    controller = ExtractBatchController(db)
    controller.delete_batch(batch_key)

@extract_batch_router.get("/{batch_key}/reconcile", response_model=PaymentReconciliationDTO)
def reconcile_extract_batch(batch_key: str, db: Session = Depends(get_db)):
    controller = ExtractBatchController(db)
    return controller.reconcile_batch(batch_key)

@extract_batch_router.post("/{batch_key}/upload-receipt", response_model=ExtractBatchDTO)
def upload_batch_receipt(batch_key: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    controller = ExtractBatchController(db)
    file_bytes = file.file.read()
    return controller.upload_receipt(batch_key=batch_key, file_bytes=file_bytes, content_type=file.content_type)



@extract_batch_router.get("/{batch_key}/extracts/{extract_key}", response_model=ExtractDTO)
def get_individual_extract(batch_key: str, extract_key: str, db: Session = Depends(get_db)):
    controller = ExtractController(db)
    return controller.get_extract(batch_key, extract_key)

@extract_batch_router.delete("/{batch_key}/extracts/{extract_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_individual_extract(batch_key: str, extract_key: str, db: Session = Depends(get_db)):
    controller = ExtractController(db)
    controller.delete_extract(batch_key, extract_key)
