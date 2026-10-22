from fastapi import Depends
from sqlalchemy.orm import Session

from src.controller.property_controller import PropertyController
from src.database.config import get_db
from src.repository.owner_repository import OwnerRepository
from src.repository.property_repository import PropertyRepository


def get_property_controller(
    db: Session = Depends(get_db),
) -> PropertyController:
    return PropertyController(
        property_repository=PropertyRepository(db),
        owner_repository=OwnerRepository(db),
    )
