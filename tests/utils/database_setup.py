from sqlalchemy.orm import Session
from src.models import ContractStatusModel

def seed_enumerators(db: Session):
    default_contract_statuses = ["active", "inactive", "pending", "canceled"]

    for value in default_contract_statuses:
        db.add(ContractStatusModel(enumerator=value))

    db.commit()