import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.environ["DATABASE_URL"] = "sqlite:///./dev_local.db"
os.environ["JWT_SECRET"] = "local-dev-jwt-secret-key-123456789"

from src.models.base import Base
from src.database.config import engine, SessionLocal
from src.scripts.seed_local import seed_all

def setup_local_environment():
    print("==================================================")
    print("[*] Inicializando Ambiente Local Seguro (Nao Persistente)")
    print("[*] Banco de Dados: SQLite (dev_local.db)")
    print("==================================================")
    
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        seed_all(db)
    finally:
        db.close()

if __name__ == "__main__":
    setup_local_environment()
    
    import uvicorn
    print("\n[*] Iniciando servidor FastAPI em http://127.0.0.1:8000 ...")
    uvicorn.run("src.app:app", host="127.0.0.1", port=8000, reload=True)
