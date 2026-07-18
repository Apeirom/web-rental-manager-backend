from fastapi import FastAPI, Depends, status, Request, HTTPException, APIRouter, UploadFile, File
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from src.database.config import get_db, engine
from src.utils.security import get_user_info_by_token
from src.models.base import Base
from src.middlewares.auth_middleware import AuthMiddleware

from src.controller.health_controller import HealthController

from src.schemas.user_schema import UserCreateSchema, UserLoginSchema, UserUpdateSchema, UserRoleUpdateSchema
from src.dto.user_dto import UserDTO, LoginResponseDTO
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
from src.dto.payment_dto import PaymentDTO, PaymentReconciliationDTO
from src.controller.payment_controller import PaymentController

from src.schemas.extract_batch_schema import ExtractBatchCreateSchema, ExtractBatchUpdateSchema
from src.dto.extract_batch_dto import ExtractBatchDTO
from src.dto.extract_dto import ExtractDTO
from src.controller.extract_batch_controller import ExtractBatchController
from src.controller.extract_controller import ExtractController

from src.controller.analysis_controller import AnalysisController
from src.dto.analysis_dto import IncomeTaxRowDTO

from src.dto.paginated_response import PaginatedResponseDTO


Base.metadata.create_all(bind=engine)

bearer_scheme = HTTPBearer()


app = FastAPI(
    title="Rental Manager API",
    description="API robusta para gestão de inquilinos, imóveis e contratos.",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "https://web-rental-manager-frontend.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@auth_router.post("/auth/login", response_model=LoginResponseDTO)
def login(schema: UserLoginSchema, db: Session = Depends(get_db)):
    controller = UserController(db)
    return controller.login(schema)



users_router = APIRouter(
    prefix="/users",
    tags=["2 Usuários"],
    dependencies=[Depends(bearer_scheme)]
)

@users_router.post("/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
def register_user(
    schema: UserCreateSchema, 
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(get_user_info_by_token)
):
    controller = UserController(db)
    return controller.register(current_user_data, schema)

@users_router.put("/me", response_model=UserDTO)
def update_my_profile(
    schema: UserUpdateSchema, 
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(get_user_info_by_token)
):
    controller = UserController(db)
    return controller.update_me(current_user_data["key"], schema)

@users_router.get("", response_model=PaginatedResponseDTO[UserDTO])
def list_users(
    skip: int = 0, 
    limit: int = 10, 
    search_term: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(get_user_info_by_token)
):        
    controller = UserController(db)
    return controller.get_paginated_users(current_user_data, skip, limit, search_term)

@users_router.patch("/{user_key}/role", response_model=UserDTO)
def update_user_role(
    user_key: str, 
    schema: UserRoleUpdateSchema, 
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(get_user_info_by_token)
):      
    controller = UserController(db)
    return controller.update_role(current_user_data, user_key, schema)



tenant_router = APIRouter(
    prefix="/tenants",
    tags=["3. Inquilinos (Tenants)"],
    dependencies=[Depends(bearer_scheme)]
)

@tenant_router.post("", response_model=TenantDTO, status_code=status.HTTP_201_CREATED)
def create_tenant(schema: TenantCreateSchema, db: Session = Depends(get_db)):
    controller = TenantController(db)
    return controller.create_tenant(schema)

@tenant_router.get("", response_model=PaginatedResponseDTO[TenantDTO])
def list_tenants(
    skip: int = 0, 
    limit: int = 10, 
    search_term: Optional[str] = None,
    name: Optional[str] = None,
    document_number: Optional[str] = None,
    only_active_contracts: bool = False,
    db: Session = Depends(get_db)
):
    controller = TenantController(db)
    return controller.get_paginated_tenants(skip, limit, search_term, name, document_number, only_active_contracts)

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
    tags=["4. Imóveis (Properties)"],
    dependencies=[Depends(bearer_scheme)]
)

@property_router.post("", response_model=PropertyDTO, status_code=status.HTTP_201_CREATED)
def create_property(schema: PropertyCreateSchema, db: Session = Depends(get_db)):
    controller = PropertyController(db)
    return controller.create_property(schema)

@property_router.get("", response_model=PaginatedResponseDTO[PropertyDTO])
def list_properties(
    skip: int = 0, 
    limit: int = 10, 
    search_term: Optional[str] = None,
    property_name: Optional[str] = None,
    owner_name: Optional[str] = None,
    only_active_contracts: bool = False,
    db: Session = Depends(get_db)
):
    controller = PropertyController(db)
    return controller.get_paginated_properties(skip, limit, search_term, property_name, owner_name, only_active_contracts)

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
    tags=["5. Imobiliárias (Real Estates)"],
    dependencies=[Depends(bearer_scheme)]
)

@real_estate_router.post("", response_model=RealEstateDTO, status_code=status.HTTP_201_CREATED)
def create_real_estate(schema: RealEstateCreateSchema, db: Session = Depends(get_db)):
    controller = RealEstateController(db)
    return controller.create_real_estate(schema)

@real_estate_router.get("", response_model=PaginatedResponseDTO[RealEstateDTO])
def list_real_estates(
    skip: int = 0, 
    limit: int = 10, 
    search_term: Optional[str] = None,
    name: Optional[str] = None,
    cnpj: Optional[str] = None,
    only_active_contracts: bool = False,
    db: Session = Depends(get_db)
):
    controller = RealEstateController(db)
    return controller.get_paginated_real_estates(skip, limit, search_term, name, cnpj, only_active_contracts)

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
    tags=["6. Fiadores (Guarantors)"],
    dependencies=[Depends(bearer_scheme)]
)

@guarantor_router.post("", response_model=GuarantorDTO, status_code=status.HTTP_201_CREATED)
def create_guarantor(schema: GuarantorCreateSchema, db: Session = Depends(get_db)):
    controller = GuarantorController(db)
    return controller.create_guarantor(schema)

@guarantor_router.get("", response_model=PaginatedResponseDTO[GuarantorDTO])
def list_guarantors(
    skip: int = 0, 
    limit: int = 10, 
    search_term: Optional[str] = None,
    name: Optional[str] = None,
    document_number: Optional[str] = None,
    only_active_contracts: bool = False,
    db: Session = Depends(get_db)
):
    controller = GuarantorController(db)
    return controller.get_paginated_guarantors(skip, limit, search_term, name, document_number, only_active_contracts)

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
    tags=["7. Seguros Fiança (Bail Insurances)"],
    dependencies=[Depends(bearer_scheme)]
)

@bail_insurance_router.post("", response_model=BailInsuranceDTO, status_code=status.HTTP_201_CREATED)
def create_bail_insurance(schema: BailInsuranceCreateSchema, db: Session = Depends(get_db)):
    controller = BailInsuranceController(db)
    return controller.create_bail_insurance(schema)

@bail_insurance_router.get("", response_model=PaginatedResponseDTO[BailInsuranceDTO])
def list_bail_insurances(
    skip: int = 0, 
    limit: int = 10, 
    search_term: Optional[str] = None,
    insurance_company: Optional[str] = None,
    validity: Optional[str] = None,
    only_active_contracts: bool = False,
    db: Session = Depends(get_db)
):
    controller = BailInsuranceController(db)
    return controller.get_paginated_bail_insurances(skip, limit, search_term, insurance_company, validity, only_active_contracts)

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
    tags=["8. Contratos (Contracts)"],
    dependencies=[Depends(bearer_scheme)]
)

@contract_router.post("", response_model=ContractDTO, status_code=status.HTTP_201_CREATED)
def create_contract(
    schema: ContractCreateSchema, 
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(get_user_info_by_token)
):
    controller = ContractController(db)
    return controller.create_contract(schema, current_user_data)

@contract_router.get("/{contract_key}", response_model=ContractDTO)
def get_contract(contract_key: str, db: Session = Depends(get_db)):
    controller = ContractController(db)
    return controller.get_contract(contract_key)

@contract_router.put("/{contract_key}", response_model=ContractDTO)
def update_contract(
    contract_key: str, 
    schema: ContractUpdateSchema, 
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(get_user_info_by_token)
):
    controller = ContractController(db)
    return controller.update_contract(contract_key, schema, current_user_data)

@contract_router.delete("/{contract_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(contract_key: str, db: Session = Depends(get_db)):
    controller = ContractController(db)
    controller.delete_contract(contract_key)

@contract_router.post("/{contract_key}/upload-document", response_model=ContractDTO)
def upload_contract_document(
    contract_key: str, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    controller = ContractController(db)
    file_bytes = file.file.read()
    return controller.upload_document(
        contract_key=contract_key, 
        file_bytes=file_bytes, 
        content_type=file.content_type
    )

@contract_router.get("", response_model=PaginatedResponseDTO[ContractDTO])
def list_contracts(
    skip: int = 0, 
    limit: int = 10,
    search_term: Optional[str] = None,
    room_name: Optional[str] = None,
    property_name: Optional[str] = None,
    tenant_name: Optional[str] = None,
    real_estate_name: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    controller = ContractController(db)
    return controller.get_paginated_contracts(
        skip, limit, search_term, room_name, property_name, tenant_name, real_estate_name, status
    )



payment_router = APIRouter(
    prefix="/payments",
    tags=["9. Pagamentos (Payments)"],
    dependencies=[Depends(bearer_scheme)]
)

@payment_router.post("", response_model=PaymentDTO, status_code=status.HTTP_201_CREATED)
def create_payment(schema: PaymentCreateSchema, db: Session = Depends(get_db)):
    controller = PaymentController(db)
    return controller.create_payment(schema)

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

@payment_router.get("", response_model=PaginatedResponseDTO[PaymentDTO], response_model_exclude_none=True)
def list_payments(
    skip: int = 0, 
    limit: int = 10, 
    amount: Optional[float] = None,          
    start_date: Optional[str] = None,      
    end_date: Optional[str] = None,
    is_linked: Optional[bool] = None,            
    db: Session = Depends(get_db)
):
    controller = PaymentController(db)
    return controller.get_paginated_payments(skip, limit, amount, start_date, end_date, is_linked)



extract_batch_router = APIRouter(
    prefix="/extract-batches",
    tags=["10. Lotes de Extratos (Extract Batches)"],
    dependencies=[Depends(bearer_scheme)]
)

@extract_batch_router.post("", response_model=ExtractBatchDTO, status_code=status.HTTP_201_CREATED)
def create_extract_batch(schema: ExtractBatchCreateSchema, db: Session = Depends(get_db)):
    controller = ExtractBatchController(db)
    return controller.create_batch(schema)

@extract_batch_router.get("", response_model=PaginatedResponseDTO[ExtractBatchDTO])
def list_extract_batches(
    skip: int = 0, 
    limit: int = 10, 
    search_term: Optional[str] = None,
    only_active_contracts: bool = False,
    is_reconciled: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    controller = ExtractBatchController(db)
    return controller.get_paginated_batches(skip, limit, search_term, only_active_contracts, is_reconciled)

@extract_batch_router.put("/{batch_key}", response_model=ExtractBatchDTO)
def update_extract_batch(batch_key: str, schema: ExtractBatchUpdateSchema, db: Session = Depends(get_db)):
    controller = ExtractBatchController(db)
    return controller.update_batch(batch_key, schema)

@extract_batch_router.delete("/{batch_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_extract_batch(batch_key: str, db: Session = Depends(get_db)):
    controller = ExtractBatchController(db)
    controller.delete_batch(batch_key)

@extract_batch_router.get("/{batch_key}/reconcile", response_model=PaymentReconciliationDTO)
def reconcile_extract_batch(batch_key: str, db: Session = Depends(get_db)):
    controller = ExtractBatchController(db)
    return controller.reconcile_batch(batch_key)

@extract_batch_router.post("/{batch_key}/upload-receipt", response_model=ExtractBatchDTO)
def upload_batch_receipt(batch_key: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    controller = ExtractBatchController(db)
    file_bytes = file.file.read()
    return controller.upload_receipt(batch_key=batch_key, file_bytes=file_bytes, content_type=file.content_type)



@extract_batch_router.get("/{batch_key}/extracts/{extract_key}", response_model=ExtractDTO)
def get_individual_extract(batch_key: str, extract_key: str, db: Session = Depends(get_db)):
    controller = ExtractController(db)
    return controller.get_extract(batch_key, extract_key)

@extract_batch_router.delete("/{batch_key}/extracts/{extract_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_individual_extract(batch_key: str, extract_key: str, db: Session = Depends(get_db)):
    controller = ExtractController(db)
    controller.delete_extract(batch_key, extract_key)



analysis_router = APIRouter(
    prefix="/analyses",
    tags=["11. Análises (Analyses)"],
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
app.include_router(users_router)
app.include_router(tenant_router)
app.include_router(property_router)
app.include_router(real_estate_router)
app.include_router(guarantor_router)
app.include_router(bail_insurance_router)
app.include_router(contract_router)
app.include_router(payment_router)
app.include_router(extract_batch_router)
app.include_router(analysis_router)