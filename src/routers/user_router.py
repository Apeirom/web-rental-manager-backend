from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from src.database.config import get_db
from typing import Optional

from src.dto.paginated_response import PaginatedResponseDTO
from src.dto.user_dto import UserDTO
from src.schemas.user_schema import UserCreateSchema, UserUpdateSchema, UserRoleUpdateSchema
from src.controller.user_controller import UserController

from src.utils.security import get_user_info_by_token

bearer_scheme = HTTPBearer()

users_router = APIRouter(
    prefix="/users",
    tags=["2 Usuários"],
    dependencies=[Depends(bearer_scheme)]
)

@users_router.post("/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
def register_user(
    schema: UserCreateSchema, 
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(get_user_info_by_token)
):
    controller = UserController(db)
    return controller.register(current_user_data, schema)

@users_router.put("/me", response_model=UserDTO)
def update_my_profile(
    schema: UserUpdateSchema, 
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(get_user_info_by_token)
):
    controller = UserController(db)
    return controller.update_me(current_user_data["key"], schema)

@users_router.get("", response_model=PaginatedResponseDTO[UserDTO])
def list_users(
    skip: int = 0, 
    limit: int = 10, 
    search_term: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(get_user_info_by_token)
):        
    controller = UserController(db)
    return controller.get_paginated_users(current_user_data, skip, limit, search_term)

@users_router.patch("/{user_key}/role", response_model=UserDTO)
def update_user_role(
    user_key: str, 
    schema: UserRoleUpdateSchema, 
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(get_user_info_by_token)
):      
    controller = UserController(db)
    return controller.update_role(current_user_data, user_key, schema)