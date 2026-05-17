import uuid
from sqlalchemy import Column, Integer, String
from src.models.base import Base

class PropertyModel(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    property_name = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    room_count = Column(Integer, default=0, nullable=False)