from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.constants import DATABASE_URL
from src.database.url import normalize_database_url

DATABASE_URL = normalize_database_url(DATABASE_URL)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e
        
    finally:
        db.close()