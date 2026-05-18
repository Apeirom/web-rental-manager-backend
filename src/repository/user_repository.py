from sqlalchemy.orm import Session
from src.models.user_model import UserModel

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, email: str, hashed_password: str) -> UserModel:
        user = UserModel(name=name, email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_key(self, user_key: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.key == user_key).first()

    def get_by_email(self, email: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.email == email).first()