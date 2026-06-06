from sqlalchemy.orm import Session
from src.models import GuaranteeTypeModel, ContractStatusModel

def seed_enumerators(db: Session):
    default_guarantees = ["deposit", "guarantor", "bail_insurance"]
    default_contract_statuses = ["active", "inactive", "pending", "canceled"]

    for value in default_guarantees:
        db.add(GuaranteeTypeModel(enumerator=value))

    for value in default_contract_statuses:
        db.add(ContractStatusModel(enumerator=value))

    db.commit()