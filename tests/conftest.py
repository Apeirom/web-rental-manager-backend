import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app import app
from src.models.base import Base
from src.models import UserModel 
from src.database.config import get_db
from src.utils.security import create_access_token
from tests.utils.database_setup import seed_enumerators


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        seed_enumerators(db)
    finally:
        db.close()
        
    yield
    
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_client(client, db_session):
    master_user = UserModel(
        key="test-key",
        name="Admin Test",
        email="admin@test.com",
        role="master",
        hashed_password="fakehashedpassword"
    )
    db_session.add(master_user)
    db_session.commit()

    token = create_access_token({"key": "test-key", "email": "admin@test.com", "role": "master"})
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    return client