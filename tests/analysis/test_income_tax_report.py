import pytest

@pytest.fixture
def base_contract_for_analysis(auth_client):
    tenant_res = auth_client.post("/tenants", json={
        "name": "Inquilino Analise", 
        "document_number": "111.222.333-44"
    })
    tenant_key = tenant_res.json()["key"]

    real_estate_res = auth_client.post("/real-estates", json={
        "name": "Imobiliária Analise", 
        "cnpj": "12.345.678/0001-99", 
        "commission": 0.10,
        "address": "Rua Central, 100",
        "phone": "+5511999999999"
    })
    real_estate_key = real_estate_res.json()["key"]

    test_owner_id = 999 
    prop_res = auth_client.post("/properties", json={
        "property_name": "Apartamento 101", 
        "owner_name": "Proprietário Investidor",
        "owner_id": test_owner_id, 
        "address": "Centro", 
        "room_count": 1
    })
    property_key = prop_res.json()["key"]

    contract_payload = {
        "guarantee_type": "deposit",
        "rental_deposit": 5000.00,
        "rent_amount": 2000.00,
        "property_key": property_key,
        "tenant_key": tenant_key,
        "real_estate_key": real_estate_key
    }
    contract_res = auth_client.post("/contracts", json=contract_payload)
    
    return {
        "contract_key": contract_res.json()["key"],
        "owner_id": test_owner_id,
        "tenant_name": "Inquilino Analise"
    }

@pytest.fixture
def extract_payload_factory():
    def _generator(contract_key, month, year):
        return {
            "extracts": [
                {
                    "contract_key": contract_key,
                    "month_ref": month,
                    "year_ref": year,
                    "items": [
                        {"category": "rent", "description": "Aluguel", "amount": 2000.00, "is_credit": True, "is_withheld_at_source": False},
                        {"category": "penalty", "description": "Multa Atraso", "amount": 100.00, "is_credit": True, "is_withheld_at_source": False},
                        {"category": "administration_fee", "description": "Taxa Adm", "amount": 200.00, "is_credit": False, "is_withheld_at_source": True},
                        {"category": "iptu", "description": "IPTU", "amount": 100.00, "is_credit": False, "is_withheld_at_source": True}
                    ]
                }
            ]
        }
    return _generator


def test_income_tax_calculation_default_rate(auth_client, base_contract_for_analysis, extract_payload_factory):
    payload = extract_payload_factory(base_contract_for_analysis["contract_key"], 1, 2026)
    auth_client.post("/extract-batches", json=payload)

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

def test_income_tax_calculation_custom_rate(auth_client, base_contract_for_analysis, extract_payload_factory):
    payload = extract_payload_factory(base_contract_for_analysis["contract_key"], 2, 2026)
    auth_client.post("/extract-batches", json=payload)

    response = auth_client.get("/analyses/income-tax?start_year=2026&start_month=1&end_year=2026&end_month=12&tax_rate=15.0")
    
    assert response.status_code == 200
    row = next(r for r in response.json() if r["reference_date"] == "02/2026" and r["tenant_name"] == "Inquilino Analise")
    
    assert row["tax_rate_used"] == 15.0
    assert row["calculated_tax"] == 270.00

# def test_income_tax_owner_filter(auth_client, base_contract_for_analysis, extract_payload_factory):
#     # 1. Popula o banco com extrato no mês 3
#     payload = extract_payload_factory(base_contract_for_analysis["contract_key"], 3, 2026)
#     auth_client.post("/extract-batches", json=payload)
    
#     valid_owner = base_contract_for_analysis["owner_id"]
#     invalid_owner = 999999 # ID que sabemos que não possui extratos

#     # 2. Testa passando um owner_id incorreto/vazio
#     res_empty = auth_client.get(f"/analyses/income-tax?start_year=2026&start_month=1&end_year=2026&end_month=12&owner_id={invalid_owner}")
#     assert res_empty.status_code == 200
#     # Verifica que nosso extrato do mês 3 não está na resposta (ou a resposta é vazia)
#     assert not any(r["reference_date"] == "03/2026" for r in res_empty.json())

#     # 3. Testa passando o owner_id correto
#     res_valid = auth_client.get(f"/analyses/income-tax?start_year=2026&start_month=1&end_year=2026&end_month=12&owner_id={valid_owner}")
#     assert res_valid.status_code == 200
#     assert any(r["reference_date"] == "03/2026" for r in res_valid.json())

def test_income_tax_empty_result(auth_client):
    response = auth_client.get("/analyses/income-tax?start_year=2030&start_month=1&end_year=2030&end_month=12")
    
    assert response.status_code == 200
    assert response.json() == []