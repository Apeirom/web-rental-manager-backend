from fastapi import Depends
from sqlalchemy.orm import Session

from src.controller.income_tax_controller import IncomeTaxController
from src.database.config import get_db
from src.repository.income_tax_repository import IncomeTaxRepository
from src.repository.owner_repository import OwnerRepository


def get_income_tax_controller(
    db: Session = Depends(get_db),
) -> IncomeTaxController:
    return IncomeTaxController(
        owner_repository=OwnerRepository(db),
        income_tax_repository=IncomeTaxRepository(db),
    )
