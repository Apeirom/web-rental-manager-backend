import uuid
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class PaymentModel(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    payment_date = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    extract_id = Column(Integer, ForeignKey("extracts.id"), nullable=True, unique=True)
    extract = relationship("ExtractModel", back_populates="payment")

    @property
    def status(self) -> str:
        return 'linked' if self.extract_id else 'unlinked'

    @property
    def extract_key(self) -> str | None:
        return self.extract.key if self.extract else None