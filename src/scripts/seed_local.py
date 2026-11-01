import sys
from sqlalchemy.orm import Session
from src.models import (
    ContractStatusModel,
    ExtractItemCategoryModel,
    UserModel,
    RealEstateModel,
    OwnerModel,
    TenantModel,
    PropertyModel,
    EquityParticipationModel,
    DepositModel,
    BailInsuranceModel,
    ContractModel,
    ExtractBatchModel,
    ExtractModel,
    ExtractItemModel,
    PaymentModel,
)
from src.utils.security import get_password_hash

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def seed_all(db: Session):
    print("[*] Iniciando populacao de seeds locais...")

    contract_statuses = ["active", "inactive", "pending", "canceled"]
    status_map = {}
    for st in contract_statuses:
        status_obj = db.query(ContractStatusModel).filter_by(enumerator=st).first()
        if not status_obj:
            status_obj = ContractStatusModel(enumerator=st)
            db.add(status_obj)
            db.flush()
        status_map[st] = status_obj

    extract_categories = [
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
        "others",
    ]
    category_map = {}
    for cat in extract_categories:
        cat_obj = db.query(ExtractItemCategoryModel).filter_by(enumerator=cat).first()
        if not cat_obj:
            cat_obj = ExtractItemCategoryModel(enumerator=cat)
            db.add(cat_obj)
            db.flush()
        category_map[cat] = cat_obj

    admin_email = "admin@rentalmanager.com"
    admin_user = db.query(UserModel).filter_by(email=admin_email).first()
    if not admin_user:
        admin_user = UserModel(
            name="Administrador Master",
            email=admin_email,
            hashed_password=get_password_hash("admin123"),
            role="master",
        )
        db.add(admin_user)
        db.flush()

    real_estate = db.query(RealEstateModel).filter_by(cnpj="12.345.678/0001-90").first()
    if not real_estate:
        real_estate = RealEstateModel(
            name="Imobiliaria Central",
            cnpj="12.345.678/0001-90",
            address="Rua Central, 100",
            commission=10.0,
            phone="(11) 99999-0001",
        )
        db.add(real_estate)
        db.flush()

    owner1 = db.query(OwnerModel).filter_by(document_number="123.456.789-00").first()
    if not owner1:
        owner1 = OwnerModel(
            name="Carlos Drummond",
            document_number="123.456.789-00",
        )
        db.add(owner1)
        db.flush()

    owner2 = db.query(OwnerModel).filter_by(document_number="987.654.321-99").first()
    if not owner2:
        owner2 = OwnerModel(
            name="Clarice Lispector",
            document_number="987.654.321-99",
        )
        db.add(owner2)
        db.flush()

    tenant1 = db.query(TenantModel).filter_by(document_number="529.982.247-25").first()
    if not tenant1:
        tenant1 = TenantModel(
            name="Machado de Assis",
            document_number="529.982.247-25",
        )
        db.add(tenant1)
        db.flush()

    tenant2 = db.query(TenantModel).filter_by(document_number="111.444.777-35").first()
    if not tenant2:
        tenant2 = TenantModel(
            name="Guimaraes Rosa",
            document_number="111.444.777-35",
        )
        db.add(tenant2)
        db.flush()

    prop1 = db.query(PropertyModel).filter_by(property_name="Apartamento Jardins 101").first()
    if not prop1:
        prop1 = PropertyModel(
            property_name="Apartamento Jardins 101",
            address="Av. Paulista, 1000 - Apto 101",
            room_count=3,
        )
        db.add(prop1)
        db.flush()
        db.add(EquityParticipationModel(property_id=prop1.id, owner_id=owner1.id, participation_percentage=60.00))
        db.add(EquityParticipationModel(property_id=prop1.id, owner_id=owner2.id, participation_percentage=40.00))
        db.flush()

    prop2 = db.query(PropertyModel).filter_by(property_name="Casa Vila Madalena").first()
    if not prop2:
        prop2 = PropertyModel(
            property_name="Casa Vila Madalena",
            address="Rua Harmonia, 500",
            room_count=4,
        )
        db.add(prop2)
        db.flush()
        db.add(EquityParticipationModel(property_id=prop2.id, owner_id=owner1.id, participation_percentage=100.00))
        db.flush()

    guarantee1 = DepositModel(amount=3000.00)
    db.add(guarantee1)
    db.flush()

    guarantee2 = BailInsuranceModel(value=5000.00, validity="2027-12-31", insurance_company="Porto Seguro")
    db.add(guarantee2)
    db.flush()

    contract1 = db.query(ContractModel).filter_by(room_name="Apto 101").first()
    if not contract1:
        contract1 = ContractModel(
            rent_amount=2500.00,
            room_name="Apto 101",
            rental_deposit=3000.00,
            property_id=prop1.id,
            tenant_id=tenant1.id,
            real_estate_id=real_estate.id,
            status_id=status_map["active"].id,
            guarantee_id=guarantee1.id,
        )
        db.add(contract1)
        db.flush()

    contract2 = db.query(ContractModel).filter_by(room_name="Casa Principal").first()
    if not contract2:
        contract2 = ContractModel(
            rent_amount=4000.00,
            room_name="Casa Principal",
            rental_deposit=0.0,
            property_id=prop2.id,
            tenant_id=tenant2.id,
            real_estate_id=real_estate.id,
            status_id=status_map["active"].id,
            guarantee_id=guarantee2.id,
        )
        db.add(contract2)
        db.flush()

    existing_batch = db.query(ExtractBatchModel).first()
    if not existing_batch:
        batch1 = ExtractBatchModel(total_net_transfer=2350.00)
        db.add(batch1)
        db.flush()

        extract1 = ExtractModel(
            month_ref=10,
            year_ref=2026,
            net_transfer=2350.00,
            contract_id=contract1.id,
            extract_batch_id=batch1.id,
        )
        db.add(extract1)
        db.flush()

        db.add(
            ExtractItemModel(
                extract_id=extract1.id,
                category_id=category_map["rent"].id,
                description="Aluguel Mensal",
                amount=2500.00,
                is_credit=True,
                is_withheld_at_source=False,
            )
        )
        db.add(
            ExtractItemModel(
                extract_id=extract1.id,
                category_id=category_map["administration_fee"].id,
                description="Taxa de Administracao",
                amount=150.00,
                is_credit=False,
                is_withheld_at_source=True,
            )
        )
        db.flush()

    payment1 = db.query(PaymentModel).filter_by(payment_date="2026-10-10", amount=2500.00).first()
    if not payment1:
        payment1 = PaymentModel(payment_date="2026-10-10", amount=2500.00)
        db.add(payment1)

    payment2 = db.query(PaymentModel).filter_by(payment_date="2026-10-15", amount=1500.00).first()
    if not payment2:
        payment2 = PaymentModel(payment_date="2026-10-15", amount=1500.00)
        db.add(payment2)

    db.commit()
    print("[+] Seeds locais populados com sucesso!")
    print(f"[*] Usuario Master: {admin_email} | Senha: admin123")
