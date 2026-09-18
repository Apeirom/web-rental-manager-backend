from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from src.database.config import get_db
from src.utils.rate_limit import limiter


from src.dto.user_dto import LoginResponseDTO
from src.schemas.user_schema import UserLoginSchema
from src.controller.user_controller import UserController

auth_router = APIRouter(
    tags=["1. Autenticação e Usuários"]
)

@auth_router.post("/auth/login", response_model=LoginResponseDTO)
@limiter.limit("5/minute")
def login(request: Request, schema: UserLoginSchema, db: Session = Depends(get_db)):
    controller = UserController(db)
    return controller.login(schema)