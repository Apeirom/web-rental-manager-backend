from sqlalchemy.orm import Session
from src.models.guarantee_type_model import GuaranteeTypeModel
from src.models.contract_status_model import ContractStatusModel

def seed_enumerators(db: Session):
    default_guarantees = ["deposit", "guarantor", "bail_insurance"]
    default_statuses = ["active", "inactive", "pending", "canceled"]

    for value in default_guarantees:
        db.add(GuaranteeTypeModel(enumerator=value))

    for value in default_statuses:
        db.add(ContractStatusModel(enumerator=value))

    db.commit()