from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

class CustomBase:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


Base = declarative_base(cls=CustomBase)