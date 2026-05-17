from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session

from src.utils.database import get_db, engine
from src.models.base import Base

from src.controller.health_controller import HealthController

from src.schemas.tenant_schema import TenantCreateSchema, TenantUpdateSchema
from src.dto.tenant_dto import TenantDTO
from src.controller.tenant_controller import TenantController

from src.schemas.property_schema import PropertyCreateSchema, PropertyUpdateSchema
from src.dto.property_dto import PropertyDTO
from src.controller.property_controller import PropertyController

from src.schemas.real_estate_schema import RealEstateCreateSchema, RealEstateUpdateSchema
from src.dto.real_estate_dto import RealEstateDTO
from src.controller.real_estate_controller import RealEstateController

from src.schemas.guarantor_schema import GuarantorCreateSchema, GuarantorUpdateSchema
from src.dto.guarantor_dto import GuarantorDTO
from src.controller.guarantor_controller import GuarantorController

from src.schemas.bail_insurance_schema import BailInsuranceCreateSchema, BailInsuranceUpdateSchema
from src.dto.bail_insurance_dto import BailInsuranceDTO
from src.controller.bail_insurance_controller import BailInsuranceController

from src.schemas.contract_schema import ContractCreateSchema, ContractUpdateSchema
from src.dto.contract_dto import ContractDTO
from src.controller.contract_controller import ContractController

from src.schemas.payment_schema import PaymentCreateSchema, PaymentUpdateSchema
from src.dto.payment_dto import PaymentDTO
from src.controller.payment_controller import PaymentController

from src.schemas.extract_schema import ExtractCreateSchema, ExtractUpdateSchema
from src.dto.extract_dto import ExtractDTO
from src.controller.extract_controller import ExtractController

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    controller = HealthController(db)
    return controller.check_status()



@app.post("/tenants", response_model=TenantDTO, status_code=status.HTTP_201_CREATED)
def create_tenant(schema: TenantCreateSchema, db: Session = Depends(get_db)):
    controller = TenantController(db)
    return controller.create_tenant(schema)

@app.get("/tenants", response_model=list[TenantDTO])
def list_tenants(db: Session = Depends(get_db)):
    controller = TenantController(db)
    return controller.get_all_tenants()

@app.get("/tenants/{tenant_key}", response_model=TenantDTO)
def get_tenant(tenant_key: str, db: Session = Depends(get_db)):
    controller = TenantController(db)
    return controller.get_tenant(tenant_key)

@app.put("/tenants/{tenant_key}", response_model=TenantDTO)
def update_tenant(tenant_key: str, schema: TenantUpdateSchema, db: Session = Depends(get_db)):
    controller = TenantController(db)
    return controller.update_tenant(tenant_key, schema)

@app.delete("/tenants/{tenant_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(tenant_key: str, db: Session = Depends(get_db)):
    controller = TenantController(db)
    controller.delete_tenant(tenant_key)



@app.post("/properties", response_model=PropertyDTO, status_code=status.HTTP_201_CREATED)
def create_property(schema: PropertyCreateSchema, db: Session = Depends(get_db)):
    controller = PropertyController(db)
    return controller.create_property(schema)

@app.get("/properties", response_model=list[PropertyDTO])
def list_properties(db: Session = Depends(get_db)):
    controller = PropertyController(db)
    return controller.get_all_properties()

@app.get("/properties/{property_key}", response_model=PropertyDTO)
def get_property(property_key: str, db: Session = Depends(get_db)):
    controller = PropertyController(db)
    return controller.get_property(property_key)

@app.put("/properties/{property_key}", response_model=PropertyDTO)
def update_property(property_key: str, schema: PropertyUpdateSchema, db: Session = Depends(get_db)):
    controller = PropertyController(db)
    return controller.update_property(property_key, schema)

@app.delete("/properties/{property_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(property_key: str, db: Session = Depends(get_db)):
    controller = PropertyController(db)
    controller.delete_property(property_key)



@app.post("/real-estates", response_model=RealEstateDTO, status_code=status.HTTP_201_CREATED)
def create_real_estate(schema: RealEstateCreateSchema, db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    return controller.create_real_estate(schema)

@app.get("/real-estates", response_model=list[RealEstateDTO])
def list_real_estates(db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    return controller.get_all_real_estates()

@app.get("/real-estates/{real_estate_key}", response_model=RealEstateDTO)
def get_real_estate(real_estate_key: str, db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    return controller.get_real_estate(real_estate_key)

@app.put("/real-estates/{real_estate_key}", response_model=RealEstateDTO)
def update_real_estate(real_estate_key: str, schema: RealEstateUpdateSchema, db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    return controller.update_real_estate(real_estate_key, schema)

@app.delete("/real-estates/{real_estate_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_real_estate(real_estate_key: str, db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    controller.delete_real_estate(real_estate_key)



@app.post("/guarantors", response_model=GuarantorDTO, status_code=status.HTTP_201_CREATED)
def create_guarantor(schema: GuarantorCreateSchema, db: Session = Depends(get_db)):
    controller = GuarantorController(db)
    return controller.create_guarantor(schema)

@app.get("/guarantors", response_model=list[GuarantorDTO])
def list_guarantors(db: Session = Depends(get_db)):
    controller = GuarantorController(db)
    return controller.get_all_guarantors()

@app.get("/guarantors/{guarantor_key}", response_model=GuarantorDTO)
def get_guarantor(guarantor_key: str, db: Session = Depends(get_db)):
    controller = GuarantorController(db)
    return controller.get_guarantor(guarantor_key)

@app.put("/guarantors/{guarantor_key}", response_model=GuarantorDTO)
def update_guarantor(guarantor_key: str, schema: GuarantorUpdateSchema, db: Session = Depends(get_db)):
    controller = GuarantorController(db)
    return controller.update_guarantor(guarantor_key, schema)

@app.delete("/guarantors/{guarantor_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_guarantor(guarantor_key: str, db: Session = Depends(get_db)):
    controller = GuarantorController(db)
    controller.delete_guarantor(guarantor_key)



@app.post("/bail-insurances", response_model=BailInsuranceDTO, status_code=status.HTTP_201_CREATED)
def create_bail_insurance(schema: BailInsuranceCreateSchema, db: Session = Depends(get_db)):
    controller = BailInsuranceController(db)
    return controller.create_bail_insurance(schema)

@app.get("/bail-insurances", response_model=list[BailInsuranceDTO])
def list_bail_insurances(db: Session = Depends(get_db)):
    controller = BailInsuranceController(db)
    return controller.get_all_bail_insurances()

@app.get("/bail-insurances/{bail_insurance_key}", response_model=BailInsuranceDTO)
def get_bail_insurance(bail_insurance_key: str, db: Session = Depends(get_db)):
    controller = BailInsuranceController(db)
    return controller.get_bail_insurance(bail_insurance_key)

@app.put("/bail-insurances/{bail_insurance_key}", response_model=BailInsuranceDTO)
def update_bail_insurance(bail_insurance_key: str, schema: BailInsuranceUpdateSchema, db: Session = Depends(get_db)):
    controller = BailInsuranceController(db)
    return controller.update_bail_insurance(bail_insurance_key, schema)

@app.delete("/bail-insurances/{bail_insurance_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bail_insurance(bail_insurance_key: str, db: Session = Depends(get_db)):
    controller = BailInsuranceController(db)
    controller.delete_bail_insurance(bail_insurance_key)



@app.post("/contracts", response_model=ContractDTO, status_code=status.HTTP_201_CREATED)
def create_contract(schema: ContractCreateSchema, db: Session = Depends(get_db)):
    controller = ContractController(db)
    return controller.create_contract(schema)

@app.get("/contracts", response_model=list[ContractDTO])
def list_contracts(db: Session = Depends(get_db)):
    controller = ContractController(db)
    return controller.get_all_contracts()

@app.get("/contracts/{contract_key}", response_model=ContractDTO)
def get_contract(contract_key: str, db: Session = Depends(get_db)):
    controller = ContractController(db)
    return controller.get_contract(contract_key)

@app.put("/contracts/{contract_key}", response_model=ContractDTO)
def update_contract(contract_key: str, schema: ContractUpdateSchema, db: Session = Depends(get_db)):
    controller = ContractController(db)
    return controller.update_contract(contract_key, schema)

@app.delete("/contracts/{contract_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(contract_key: str, db: Session = Depends(get_db)):
    controller = ContractController(db)
    controller.delete_contract(contract_key)



@app.post("/payments", response_model=PaymentDTO, status_code=status.HTTP_201_CREATED)
def create_payment(schema: PaymentCreateSchema, db: Session = Depends(get_db)):
    controller = PaymentController(db)
    return controller.create_payment(schema)

@app.get("/payments", response_model=list[PaymentDTO])
def list_payments(db: Session = Depends(get_db)):
    controller = PaymentController(db)
    return controller.get_all_payments()

@app.get("/payments/{payment_key}", response_model=PaymentDTO)
def get_payment(payment_key: str, db: Session = Depends(get_db)):
    controller = PaymentController(db)
    return controller.get_payment(payment_key)

@app.put("/payments/{payment_key}", response_model=PaymentDTO)
def update_payment(payment_key: str, schema: PaymentUpdateSchema, db: Session = Depends(get_db)):
    controller = PaymentController(db)
    return controller.update_payment(payment_key, schema)

@app.delete("/payments/{payment_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_key: str, db: Session = Depends(get_db)):
    controller = PaymentController(db)
    controller.delete_payment(payment_key)



@app.post("/extracts", response_model=ExtractDTO, status_code=status.HTTP_201_CREATED)
def create_extract(schema: ExtractCreateSchema, db: Session = Depends(get_db)):
    controller = ExtractController(db)
    return controller.create_extract(schema)

@app.get("/extracts", response_model=list[ExtractDTO])
def list_extracts(db: Session = Depends(get_db)):
    controller = ExtractController(db)
    return controller.get_all_extracts()

@app.get("/extracts/{extract_key}", response_model=ExtractDTO)
def get_extract(extract_key: str, db: Session = Depends(get_db)):
    controller = ExtractController(db)
    return controller.get_extract(extract_key)

@app.put("/extracts/{extract_key}", response_model=ExtractDTO)
def update_extract(extract_key: str, schema: ExtractUpdateSchema, db: Session = Depends(get_db)):
    controller = ExtractController(db)
    return controller.update_extract(extract_key, schema)

@app.delete("/extracts/{extract_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_extract(extract_key: str, db: Session = Depends(get_db)):
    controller = ExtractController(db)
    controller.delete_extract(extract_key)