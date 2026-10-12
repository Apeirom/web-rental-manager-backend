import pytest

@pytest.fixture
def base_contract_for_analysis(
    tenant_factory, real_estate_factory, property_factory, contract_factory
):
    tenant = tenant_factory(
        name="Inquilino Analise",
        document_number="111.222.333-44",
    )
    real_estate = real_estate_factory(
        name="Imobiliária Analise",
        cnpj="12.345.678/0001-99",
        commission=0.10,
        address="Rua Central, 100",
        phone="+5511999999999",
    )
    property_record = property_factory(
        property_name="Apartamento 101",
        owner_name="Proprietário Investidor",
        address="Centro",
        room_count=1,
    )
    contract = contract_factory(
        payload={
            "rent_amount": 2000.00,
            "property_key": property_record["key"],
            "tenant_key": tenant["key"],
            "real_estate_key": real_estate["key"],
        }
    )
    
    return {
        "contract_key": contract["key"],
        "tenant_name": "Inquilino Analise"
    }

def test_income_tax_calculation_default_rate(
    auth_client, base_contract_for_analysis, extract_batch_factory
):
    extract_batch_factory(
        contract_key=base_contract_for_analysis["contract_key"],
        month_ref=1,
        year_ref=2026,
        items=[
            {"category": "rent", "description": "Aluguel", "amount": 2000.00, "is_credit": True, "is_withheld_at_source": False},
            {"category": "penalty", "description": "Multa Atraso", "amount": 100.00, "is_credit": True, "is_withheld_at_source": False},
            {"category": "administration_fee", "description": "Taxa Adm", "amount": 200.00, "is_credit": False, "is_withheld_at_source": True},
            {"category": "iptu", "description": "IPTU", "amount": 100.00, "is_credit": False, "is_withheld_at_source": True},
        ],
    )

    response = auth_client.get("/analyses/income-tax?start_year=2026&start_month=1&end_year=2026&end_month=12")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    
    row = next(r for r in data if r["reference_date"] == "01/2026" and r["tenant_name"] == "Inquilino Analise")
    
    assert row["total_credits"] == 2100.00
    assert row["total_debits"] == 300.00
    assert row["tax_rate_used"] == 27.5
    
    assert row["calculated_tax"] == 495.00
    
    assert len(row["items"]) == 4
    rent_item = next(i for i in row["items"] if i["category"] == "rent")
    assert rent_item["type"] == "credit"

def test_income_tax_calculation_custom_rate(
    auth_client, base_contract_for_analysis, extract_batch_factory
):
    extract_batch_factory(
        contract_key=base_contract_for_analysis["contract_key"],
        month_ref=2,
        year_ref=2026,
        items=[
            {"category": "rent", "description": "Aluguel", "amount": 2000.00, "is_credit": True, "is_withheld_at_source": False},
            {"category": "penalty", "description": "Multa Atraso", "amount": 100.00, "is_credit": True, "is_withheld_at_source": False},
            {"category": "administration_fee", "description": "Taxa Adm", "amount": 200.00, "is_credit": False, "is_withheld_at_source": True},
            {"category": "iptu", "description": "IPTU", "amount": 100.00, "is_credit": False, "is_withheld_at_source": True},
        ],
    )

    response = auth_client.get("/analyses/income-tax?start_year=2026&start_month=1&end_year=2026&end_month=12&tax_rate=15.0")
    
    assert response.status_code == 200
    row = next(r for r in response.json() if r["reference_date"] == "02/2026" and r["tenant_name"] == "Inquilino Analise")
    
    assert row["tax_rate_used"] == 15.0
    assert row["calculated_tax"] == 270.00

def test_income_tax_empty_result(auth_client):
    response = auth_client.get("/analyses/income-tax?start_year=2030&start_month=1&end_year=2030&end_month=12")
    
    assert response.status_code == 200
    assert response.json() == []