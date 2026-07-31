from sqlalchemy import Column, Integer, String

class EnumeratorMixin:
    id = Column(Integer, primary_key=True, index=True)
    enumerator = Column(String, unique=True, nullable=False)