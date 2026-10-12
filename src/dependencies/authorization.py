from fastapi import Depends
from sqlalchemy.orm import Session

from src.controller.user_controller import UserController
from src.database.config import get_db
from src.utils.security import get_user_info_by_token


def require_master_user(
    current_user_data: dict = Depends(get_user_info_by_token),
    db: Session = Depends(get_db),
) -> None:
    UserController(db).validate_master_user(current_user_data)
