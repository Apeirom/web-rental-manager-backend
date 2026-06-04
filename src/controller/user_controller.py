from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.repository.user_repository import UserRepository
from src.schemas.user_schema import UserCreateSchema, UserLoginSchema, UserUpdateSchema, UserRoleUpdateSchema
from src.dto.user_dto import UserDTO, TokenDTO, LoginResponseDTO
from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import UserDuplicateEmailError, InvalidCredentialsError, UserNotFoundError, InvalidUserRole
from src.utils.security import get_password_hash, verify_password, create_access_token

class UserController:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def validate_master_user(self, current_user_data: dict):
        if current_user_data.get("role") != "master":
            raise InvalidUserRole()
        
        master_user_model = self.user_repository.get_by_key(current_user_data.get("key"))
        if not master_user_model:
            raise UserNotFoundError(current_user_data.get("key")) 

        if master_user_model.role != "master":
            raise InvalidUserRole()

    def register(self, current_user_data: dict, schema: UserCreateSchema) -> UserDTO:

        self.validate_master_user(current_user_data)

        existing = self.user_repository.get_by_email(schema.email)
        if existing:
            raise UserDuplicateEmailError(schema.email)

        hashed_pw = get_password_hash(schema.password)
        user_model = self.user_repository.create(
            name=schema.name,
            email=schema.email,
            hashed_password=hashed_pw
        )
        return UserDTO.model_validate(user_model)

    def login(self, schema: UserLoginSchema) -> LoginResponseDTO:
        user_model = self.user_repository.get_by_email(schema.email)
        if not user_model:
            raise InvalidCredentialsError()

        if not verify_password(schema.password, user_model.hashed_password):
            raise InvalidCredentialsError()

        token_payload = {
            "key": user_model.key, 
            "email": user_model.email,
            "role": user_model.role 
        }
        token = create_access_token(data=token_payload)
        
        return LoginResponseDTO(
            token=TokenDTO(access_token=token, token_type="bearer"),
            user=UserDTO.model_validate(user_model)
        )

    def update_me(self, current_user_key: str, schema: UserUpdateSchema) -> UserDTO:
        user_model = self.user_repository.get_by_key(current_user_key)
        if not user_model:
            raise UserNotFoundError(current_user_key)
        
        if schema.email and schema.email != user_model.email:
            existing = self.user_repository.get_by_email(schema.email)
            if existing:
                raise UserDuplicateEmailError(email=schema.email)
        
        hashed_pw = get_password_hash(schema.password) if schema.password else None
        
        updated_model = self.user_repository.update(
            user_model=user_model,
            name=schema.name,
            email=schema.email,
            hashed_password=hashed_pw
        )
        return UserDTO.model_validate(updated_model)

    def get_paginated_users(self, current_user_data: dict, skip: int, limit: int, search_term: str | None = None) -> PaginatedResponseDTO[UserDTO]:
        self.validate_master_user(current_user_data)

        total_count, user_models = self.user_repository.get_paginated(skip, limit, search_term)
        user_dtos = [UserDTO.model_validate(u) for u in user_models]
        
        return PaginatedResponseDTO(
            total=total_count,
            skip=skip,
            limit=limit,
            data=user_dtos
        )

    def update_role(self, current_user_data:dict, target_user_key: str, schema: UserRoleUpdateSchema) -> UserDTO:
        self.validate_master_user(current_user_data)

        target_user = self.user_repository.get_by_key(target_user_key)
        if not target_user:
            raise UserNotFoundError(target_user_key)
        
        updated_model = self.user_repository.update(user_model=target_user, role=schema.role)
        return UserDTO.model_validate(updated_model)