from sqlalchemy.orm import Session
from src.models import GuaranteeTypeModel, ContractStatusModel, PaymentStatusModel

def seed_enumerators(db: Session):
    default_guarantees = ["deposit", "guarantor", "bail_insurance"]
    default_contract_statuses = ["active", "inactive", "pending", "canceled"]
    dafault_payment_statuses = ["linked", "unlinked"]

    for value in default_guarantees:
        db.add(GuaranteeTypeModel(enumerator=value))

    for value in default_contract_statuses:
        db.add(ContractStatusModel(enumerator=value))

    for value in dafault_payment_statuses:
        db.add(PaymentStatusModel(enumerator=value))

    db.commit()