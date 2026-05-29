from sqlalchemy.orm import Session
from src.repository.user_repository import UserRepository
from src.schemas.user_schema import UserCreateSchema, UserLoginSchema
from src.dto.user_dto import UserDTO, TokenDTO, LoginResponseDTO
from src.errors.custom_errors import UserDuplicateEmailError, InvalidCredentialsError
from src.utils.security import get_password_hash, verify_password, create_access_token

class UserController:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def register(self, schema: UserCreateSchema) -> UserDTO:
        existing = self.user_repository.get_by_email(schema.email)
        if existing:
            raise UserDuplicateEmailError(email=schema.email)

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
            "sub": user_model.key, 
            "email": user_model.email,
            "role": user_model.role 
        }
        token = create_access_token(data=token_payload)
        
        return LoginResponseDTO(
            token=TokenDTO(access_token=token, token_type="bearer"),
            user=UserDTO.model_validate(user_model)
        )