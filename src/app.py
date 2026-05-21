from fastapi import FastAPI, Depends, status, Request, HTTPException, APIRouter
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.utils.database import get_db, engine
from src.models.base import Base
from src.middlewares.auth_middleware import AuthMiddleware

from src.controller.health_controller import HealthController

from src.schemas.user_schema import UserCreateSchema, UserLoginSchema
from src.dto.user_dto import UserDTO, TokenDTO
from src.controller.user_controller import UserController

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

from src.controller.analysis_controller import AnalysisController
from src.dto.analysis_dto import IncomeTaxRowDTO


Base.metadata.create_all(bind=engine)


bearer_scheme = HTTPBearer()


app = FastAPI(
    title="Rental Manager API",
    description="API robusta para gestão de inquilinos, imóveis e contratos.",
    version="1.0.0"
)


app.add_middleware(AuthMiddleware)



@app.get("/", tags=["0. Monitoramento e Sistema"])
def root():
    return {"status": "Rental Manager API is online"}


@app.get("/health", tags=["0. Monitoramento e Sistema"])
def health_check(db: Session = Depends(get_db)):
    controller = HealthController(db)
    return controller.check_status()



auth_router = APIRouter(
    tags=["1. Autenticação e Usuários"]
)

@auth_router.post("/users/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
def register_user(schema: UserCreateSchema, request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    if current_user.get("role") != "master":
        raise HTTPException(status_code=403, detail="Apenas usuários master podem registrar novos usuários")

    controller = UserController(db)
    return controller.register(schema)

@auth_router.post("/auth/login", response_model=TokenDTO)
def login(schema: UserLoginSchema, db: Session = Depends(get_db)):
    controller = UserController(db)
    return controller.login(schema)



tenant_router = APIRouter(
    prefix="/tenants",
    tags=["2. Inquilinos (Tenants)"],
    dependencies=[Depends(bearer_scheme)]
)

@tenant_router.post("", response_model=TenantDTO, status_code=status.HTTP_201_CREATED)
def create_tenant(schema: TenantCreateSchema, db: Session = Depends(get_db)):
    controller = TenantController(db)
    return controller.create_tenant(schema)

@tenant_router.get("", response_model=list[TenantDTO])
def list_tenants(db: Session = Depends(get_db)):
    controller = TenantController(db)
    return controller.get_all_tenants()

@tenant_router.get("/{tenant_key}", response_model=TenantDTO)
def get_tenant(tenant_key: str, db: Session = Depends(get_db)):
    controller = TenantController(db)
    return controller.get_tenant(tenant_key)


@tenant_router.put("/{tenant_key}", response_model=TenantDTO)
def update_tenant(tenant_key: str, schema: TenantUpdateSchema, db: Session = Depends(get_db)):
    controller = TenantController(db)
    return controller.update_tenant(tenant_key, schema)

@tenant_router.delete("/{tenant_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(tenant_key: str, db: Session = Depends(get_db)):
    controller = TenantController(db)
    controller.delete_tenant(tenant_key)



property_router = APIRouter(
    prefix="/properties",
    tags=["3. Imóveis (Properties)"],
    dependencies=[Depends(bearer_scheme)]
)

@property_router.post("", response_model=PropertyDTO, status_code=status.HTTP_201_CREATED)
def create_property(schema: PropertyCreateSchema, db: Session = Depends(get_db)):
    controller = PropertyController(db)
    return controller.create_property(schema)

@property_router.get("", response_model=list[PropertyDTO])
def list_properties(db: Session = Depends(get_db)):
    controller = PropertyController(db)
    return controller.get_all_properties()

@property_router.get("/{property_key}", response_model=PropertyDTO)
def get_property(property_key: str, db: Session = Depends(get_db)):
    controller = PropertyController(db)
    return controller.get_property(property_key)

@property_router.put("/{property_key}", response_model=PropertyDTO)
def update_property(property_key: str, schema: PropertyUpdateSchema, db: Session = Depends(get_db)):
    controller = PropertyController(db)
    return controller.update_property(property_key, schema)

@property_router.delete("/{property_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(property_key: str, db: Session = Depends(get_db)):
    controller = PropertyController(db)
    controller.delete_property(property_key)



real_estate_router = APIRouter(
    prefix="/real-estates",
    tags=["4. Imobiliárias (Real Estates)"],
    dependencies=[Depends(bearer_scheme)]
)

@real_estate_router.post("", response_model=RealEstateDTO, status_code=status.HTTP_201_CREATED)
def create_real_estate(schema: RealEstateCreateSchema, db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    return controller.create_real_estate(schema)

@real_estate_router.get("", response_model=list[RealEstateDTO])
def list_real_estates(db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    return controller.get_all_real_estates()

@real_estate_router.get("/{real_estate_key}", response_model=RealEstateDTO)
def get_real_estate(real_estate_key: str, db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    return controller.get_real_estate(real_estate_key)

@real_estate_router.put("/{real_estate_key}", response_model=RealEstateDTO)
def update_real_estate(real_estate_key: str, schema: RealEstateUpdateSchema, db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    return controller.update_real_estate(real_estate_key, schema)

@real_estate_router.delete("/{real_estate_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_real_estate(real_estate_key: str, db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    controller.delete_real_estate(real_estate_key)



guarantor_router = APIRouter(
    prefix="/guarantors",
    tags=["5. Fiadores (Guarantors)"],
    dependencies=[Depends(bearer_scheme)]
)

@guarantor_router.post("", response_model=GuarantorDTO, status_code=status.HTTP_201_CREATED)
def create_guarantor(schema: GuarantorCreateSchema, db: Session = Depends(get_db)):
    controller = GuarantorController(db)
    return controller.create_guarantor(schema)

@guarantor_router.get("", response_model=list[GuarantorDTO])
def list_guarantors(db: Session = Depends(get_db)):
    controller = GuarantorController(db)
    return controller.get_all_guarantors()

@guarantor_router.get("/{guarantor_key}", response_model=GuarantorDTO)
def get_guarantor(guarantor_key: str, db: Session = Depends(get_db)):
    controller = GuarantorController(db)
    return controller.get_guarantor(guarantor_key)

@guarantor_router.put("/{guarantor_key}", response_model=GuarantorDTO)
def update_guarantor(guarantor_key: str, schema: GuarantorUpdateSchema, db: Session = Depends(get_db)):
    controller = GuarantorController(db)
    return controller.update_guarantor(guarantor_key, schema)

@guarantor_router.delete("/{guarantor_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_guarantor(guarantor_key: str, db: Session = Depends(get_db)):
    controller = GuarantorController(db)
    controller.delete_guarantor(guarantor_key)



bail_insurance_router = APIRouter(
    prefix="/bail-insurances",
    tags=["6. Seguros Fiança (Bail Insurances)"],
    dependencies=[Depends(bearer_scheme)]
)

@bail_insurance_router.post("", response_model=BailInsuranceDTO, status_code=status.HTTP_201_CREATED)
def create_bail_insurance(schema: BailInsuranceCreateSchema, db: Session = Depends(get_db)):
    controller = BailInsuranceController(db)
    return controller.create_bail_insurance(schema)

@bail_insurance_router.get("", response_model=list[BailInsuranceDTO])
def list_bail_insurances(db: Session = Depends(get_db)):
    controller = BailInsuranceController(db)
    return controller.get_all_bail_insurances()

@bail_insurance_router.get("/{bail_insurance_key}", response_model=BailInsuranceDTO)
def get_bail_insurance(bail_insurance_key: str, db: Session = Depends(get_db)):
    controller = BailInsuranceController(db)
    return controller.get_bail_insurance(bail_insurance_key)

@bail_insurance_router.put("/{bail_insurance_key}", response_model=BailInsuranceDTO)
def update_bail_insurance(bail_insurance_key: str, schema: BailInsuranceUpdateSchema, db: Session = Depends(get_db)):
    controller = BailInsuranceController(db)
    return controller.update_bail_insurance(bail_insurance_key, schema)

@bail_insurance_router.delete("/{bail_insurance_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bail_insurance(bail_insurance_key: str, db: Session = Depends(get_db)):
    controller = BailInsuranceController(db)
    controller.delete_bail_insurance(bail_insurance_key)



contract_router = APIRouter(
    prefix="/contracts",
    tags=["7. Contratos (Contracts)"],
    dependencies=[Depends(bearer_scheme)]
)

@contract_router.post("", response_model=ContractDTO, status_code=status.HTTP_201_CREATED)
def create_contract(schema: ContractCreateSchema, db: Session = Depends(get_db)):
    controller = ContractController(db)
    return controller.create_contract(schema)

@contract_router.get("", response_model=list[ContractDTO])
def list_contracts(db: Session = Depends(get_db)):
    controller = ContractController(db)
    return controller.get_all_contracts()

@contract_router.get("/{contract_key}", response_model=ContractDTO)
def get_contract(contract_key: str, db: Session = Depends(get_db)):
    controller = ContractController(db)
    return controller.get_contract(contract_key)

@contract_router.put("/{contract_key}", response_model=ContractDTO)
def update_contract(contract_key: str, schema: ContractUpdateSchema, db: Session = Depends(get_db)):
    controller = ContractController(db)
    return controller.update_contract(contract_key, schema)

@contract_router.delete("/{contract_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(contract_key: str, db: Session = Depends(get_db)):
    controller = ContractController(db)
    controller.delete_contract(contract_key)



payment_router = APIRouter(
    prefix="/payments",
    tags=["8. Pagamentos (Payments)"],
    dependencies=[Depends(bearer_scheme)]
)

@payment_router.post("", response_model=PaymentDTO, status_code=status.HTTP_201_CREATED)
def create_payment(schema: PaymentCreateSchema, db: Session = Depends(get_db)):
    controller = PaymentController(db)
    return controller.create_payment(schema)

@payment_router.get("", response_model=list[PaymentDTO])
def list_payments(db: Session = Depends(get_db)):
    controller = PaymentController(db)
    return controller.get_all_payments()

@payment_router.get("/{payment_key}", response_model=PaymentDTO)
def get_payment(payment_key: str, db: Session = Depends(get_db)):
    controller = PaymentController(db)
    return controller.get_payment(payment_key)

@payment_router.put("/{payment_key}", response_model=PaymentDTO)
def update_payment(payment_key: str, schema: PaymentUpdateSchema, db: Session = Depends(get_db)):
    controller = PaymentController(db)
    return controller.update_payment(payment_key, schema)

@payment_router.delete("/{payment_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_key: str, db: Session = Depends(get_db)):
    controller = PaymentController(db)
    controller.delete_payment(payment_key)



extract_router = APIRouter(
    prefix="/extracts",
    tags=["9. Extratos (Extracts)"],
    dependencies=[Depends(bearer_scheme)]
)

@extract_router.post("", response_model=ExtractDTO, status_code=status.HTTP_201_CREATED)
def create_extract(schema: ExtractCreateSchema, db: Session = Depends(get_db)):
    controller = ExtractController(db)
    return controller.create_extract(schema)

@extract_router.get("", response_model=list[ExtractDTO])
def list_extracts(db: Session = Depends(get_db)):
    controller = ExtractController(db)
    return controller.get_all_extracts()

@extract_router.get("/{extract_key}", response_model=ExtractDTO)
def get_extract(extract_key: str, db: Session = Depends(get_db)):
    controller = ExtractController(db)
    return controller.get_extract(extract_key)

@extract_router.put("/{extract_key}", response_model=ExtractDTO)
def update_extract(extract_key: str, schema: ExtractUpdateSchema, db: Session = Depends(get_db)):
    controller = ExtractController(db)
    return controller.update_extract(extract_key, schema)

@extract_router.delete("/{extract_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_extract(extract_key: str, db: Session = Depends(get_db)):
    controller = ExtractController(db)
    controller.delete_extract(extract_key)



analysis_router = APIRouter(
    prefix="/analyses",
    tags=["10. Análises (Analyses)"],
    dependencies=[Depends(bearer_scheme)]
)

@analysis_router.get("/income-tax", response_model=list[IncomeTaxRowDTO])
def get_income_tax(
    start_year: int, 
    start_month: int, 
    end_year: int, 
    end_month: int, 
    db: Session = Depends(get_db)
):
    controller = AnalysisController(db)
    return controller.generate_income_tax_report(start_year, start_month, end_year, end_month)



app.include_router(auth_router)
app.include_router(tenant_router)
app.include_router(property_router)
app.include_router(real_estate_router)
app.include_router(guarantor_router)
app.include_router(bail_insurance_router)
app.include_router(contract_router)
app.include_router(payment_router)
app.include_router(extract_router)
app.include_router(analysis_router)