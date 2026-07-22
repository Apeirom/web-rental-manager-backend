from sqlalchemy import Column, Integer, String
from src.models.base import Base

class ContractStatusModel(Base):
    __tablename__ = "contract_statuses"

    id = Column(Integer, primary_key=True, index=True)
    enumerator = Column(String, unique=True, nullable=False)