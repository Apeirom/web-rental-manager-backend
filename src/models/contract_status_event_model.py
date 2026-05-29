import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship  # <-- Importação necessária
from src.models.base import Base

class ContractStatusEventModel(Base):
    __tablename__ = "contract_status_events"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    status_id = Column(Integer, ForeignKey("contract_statuses.id"), nullable=False)
    
    user_data = Column(JSON, nullable=False)

    contract = relationship("ContractModel")
    status = relationship("ContractStatusModel")