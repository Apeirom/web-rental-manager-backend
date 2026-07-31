from sqlalchemy.orm import Session
from src.models import ContractStatusModel, ExtractItemCategoryModel

def seed_enumerators(db: Session):
    default_contract_statuses = ["active", "inactive", "pending", "canceled"]
    for value in default_contract_statuses:
        db.add(ContractStatusModel(enumerator=value))

    default_extract_categories = [
        "rent", 
        "agreement", 
        "iptu", 
        "water", 
        "maintenance", 
        "penalty", 
        "interest", 
        "other_revenues", 
        "bank_fee", 
        "administration_fee", 
        "others"
    ]
    for value in default_extract_categories:
        db.add(ExtractItemCategoryModel(enumerator=value))

    db.commit()