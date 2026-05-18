from src.errors.base_error import BaseAppException

class TenantNotFoundError(BaseAppException):
    def __init__(self, tenant_key: str):
        super().__init__(
            status_code=404,
            code="RM-0001",
            message_en="Tenant with KEY {tenant_key} not found",
            message_pt="Inquilino com KEY {tenant_key} não encontrado",
            tenant_key=tenant_key
        )

class TenantDuplicateDocumentError(BaseAppException):
    def __init__(self, document_number: str):
        super().__init__(
            status_code=400,
            code="RM-0002",
            message_en="A tenant with document {document_number} already exists",
            message_pt="Um inquilino com o documento {document_number} já existe",
            document_number=document_number
        )

class PropertyNotFoundError(BaseAppException):
    def __init__(self, property_key: str):
        super().__init__(
            status_code=404,
            code="RM-0003",
            message_en="Property with KEY {property_key} not found",
            message_pt="Imóvel com KEY {property_key} não encontrado",
            property_key=property_key
        )

class RealEstateNotFoundError(BaseAppException):
    def __init__(self, real_estate_key: str):
        super().__init__(
            status_code=404,
            code="RM-0004",
            message_en="Real estate agency with KEY {real_estate_key} not found",
            message_pt="Imobiliária com KEY {real_estate_key} não encontrada",
            real_estate_key=real_estate_key
        )

class RealEstateDuplicateCnpjError(BaseAppException):
    def __init__(self, cnpj: str):
        super().__init__(
            status_code=400,
            code="RM-0005",
            message_en="A real estate agency with CNPJ {cnpj} already exists",
            message_pt="Uma imobiliária com o CNPJ {cnpj} já existe",
            cnpj=cnpj
        )

class GuarantorNotFoundError(BaseAppException):
    def __init__(self, guarantor_key: str):
        super().__init__(
            status_code=404,
            code="RM-0006",
            message_en="Guarantor with KEY {guarantor_key} not found",
            message_pt="Fiador com KEY {guarantor_key} não encontrado",
            guarantor_key=guarantor_key
        )

class GuarantorDuplicateDocumentError(BaseAppException):
    def __init__(self, document_number: str):
        super().__init__(
            status_code=400,
            code="RM-0007",
            message_en="A guarantor with document {document_number} already exists",
            message_pt="Um fiador com o documento {document_number} já existe",
            document_number=document_number
        )

class BailInsuranceNotFoundError(BaseAppException):
    def __init__(self, bail_insurance_key: str):
        super().__init__(
            status_code=404,
            code="RM-0008",
            message_en="Bail insurance with KEY {bail_insurance_key} not found",
            message_pt="Seguro fiança com KEY {bail_insurance_key} não encontrado",
            bail_insurance_key=bail_insurance_key
        )

class ContractNotFoundError(BaseAppException):
    def __init__(self, contract_key: str):
        super().__init__(
            status_code=404,
            code="RM-0009",
            message_en="Contract with KEY {contract_key} not found",
            message_pt="Contrato com KEY {contract_key} não encontrado",
            contract_key=contract_key
        )

class ContractInvalidRelationError(BaseAppException):
    def __init__(self, entity_name: str, key: str):
        super().__init__(
            status_code=400,
            code="RM-0010",
            message_en="{entity_name} with KEY {key} does not exist",
            message_pt="{entity_name} com KEY {key} não existe",
            entity_name=entity_name,
            key=key
        )

class PaymentNotFoundError(BaseAppException):
    def __init__(self, payment_key: str):
        super().__init__(
            status_code=404,
            code="RM-0011",
            message_en="Payment with KEY {payment_key} not found",
            message_pt="Pagamento com KEY {payment_key} não encontrado",
            payment_key=payment_key
        )

class PaymentInvalidRelationError(BaseAppException):
    def __init__(self, entity_name: str, key: str):
        super().__init__(
            status_code=400,
            code="RM-0012",
            message_en="{entity_name} with KEY {key} does not exist",
            message_pt="{entity_name} com KEY {key} não existe",
            entity_name=entity_name,
            key=key
        )

class ExtractNotFoundError(BaseAppException):
    def __init__(self, extract_key: str):
        super().__init__(
            status_code=404,
            code="RM-0013",
            message_en="Extract with KEY {extract_key} not found",
            message_pt="Extrato com KEY {extract_key} não encontrado",
            extract_key=extract_key
        )

class ExtractInvalidRelationError(BaseAppException):
    def __init__(self, entity_name: str, key: str):
        super().__init__(
            status_code=400,
            code="RM-0014",
            message_en="{entity_name} with KEY {key} does not exist",
            message_pt="{entity_name} com KEY {key} não existe",
            entity_name=entity_name,
            key=key
        )

class UserNotFoundError(BaseAppException):
    def __init__(self, user_key: str):
        super().__init__(
            status_code=404,
            code="RM-0015",
            message_en="User with KEY {user_key} not found",
            message_pt="Usuário com KEY {user_key} não encontrado",
            user_key=user_key
        )

class UserDuplicateEmailError(BaseAppException):
    def __init__(self, email: str):
        super().__init__(
            status_code=400,
            code="RM-0016",
            message_en="A user with email {email} already exists",
            message_pt="Um usuário com o email {email} já existe",
            email=email
        )

class InvalidCredentialsError(BaseAppException):
    def __init__(self):
        super().__init__(
            status_code=401,
            code="RM-0017",
            message_en="Invalid email or password",
            message_pt="Email ou senha inválidos"
        )