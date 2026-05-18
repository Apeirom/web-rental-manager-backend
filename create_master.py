import os
from dotenv import load_dotenv
from src.utils.database import SessionLocal
from src.models.user_model import UserModel
from src.utils.security import get_password_hash

load_dotenv()

def create_first_master():
    db = SessionLocal()
    email = input("Digite o email do admin: ")
    password = input("Digite a senha do admin: ")
    
    existing = db.query(UserModel).filter(UserModel.email == email).first()
    if existing:
        print("Usuário já existe!")
        return

    admin = UserModel(
        name="System Admin",
        email=email,
        hashed_password=get_password_hash(password),
        role="master"
    )
    
    db.add(admin)
    db.commit()
    print(f"Master {email} criado com sucesso!")
    db.close()

if __name__ == "__main__":
    create_first_master()