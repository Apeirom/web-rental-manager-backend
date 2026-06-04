from sqlalchemy.orm import Session
from src.models import UserModel
from src.repository.base_repository import BaseRepository 

class UserRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, name: str, email: str, hashed_password: str) -> UserModel:
        user = UserModel(name=name, email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.flush()
        return user

    def get_by_key(self, user_key: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.key == user_key).first()

    def get_by_email(self, email: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def update(
        self, 
        user_model: UserModel, 
        name: str | None = None, 
        email: str | None = None, 
        hashed_password: str | None = None,
        role: str | None = None
    ) -> UserModel:
        if name is not None:
            user_model.name = name
        if email is not None:
            user_model.email = email
        if hashed_password is not None:
            user_model.hashed_password = hashed_password
        if role is not None:
            user_model.role = role
            
        self.db.flush()
        return user_model

    def get_paginated(
        self, skip: int = 0, limit: int = 10, search_term: str | None = None
    ) -> tuple[int, list[UserModel]]:
        query = self.db.query(UserModel)
        
        if search_term:
            query = query.filter(
                (UserModel.name.ilike(f"%{search_term}%")) | 
                (UserModel.email.ilike(f"%{search_term}%"))
            )
            
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return total, items