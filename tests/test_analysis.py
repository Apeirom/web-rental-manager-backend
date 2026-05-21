def test_income_tax_analysis_success(auth_client):
    tenant_res = auth_client.post("/tenants", json={"name": "Inquilino Rico", "document_number": "111.222.333-44"})
    tenant_key = tenant_res.json()["key"]

    real_estate_res = auth_client.post("/real-estates", json={
        "name": "Imobiliária Central", 
        "cnpj": "12.345.678/0001-99", 
        "commission": 0.10,
        "address": "Avenida Central, 1000",
        "phone": "+5511999999999"
    })
    assert real_estate_res.status_code == 201
    real_estate_key = real_estate_res.json()["key"]

    prop_res = auth_client.post("/properties", json={"property_name": "Edifício Comercial", "owner_name": "Dono", "address": "Centro", "room_count": 1})
    assert prop_res.status_code == 201
    property_key = prop_res.json()["key"]

    contract_payload = {
        "guarantee_type": "deposit",
        "rental_deposit": 5000.00,
        "rent_amount": 2000.00,
        "room_name": "Sala 101",
        "property_key": property_key,
        "tenant_key": tenant_key,
        "real_estate_key": real_estate_key
    }
    contract_res = auth_client.post("/contracts", json=contract_payload)
    assert contract_res.status_code == 201
    contract_key = contract_res.json()["key"]

    extract_payload = {
        "contract_key": contract_key,
        "month_ref": 5,
        "year_ref": 2026,
        "rent_amount": 2000.00,
        "agreement": 500.00, # Base total = 2500
        "iptu": 100.00,
        "water": 50.00
    }
    auth_client.post("/extracts", json=extract_payload)
    response = auth_client.get("/analyses/income-tax?start_year=2026&start_month=1&end_year=2026&end_month=12")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    
    row = data[0]
    assert row["reference_date"] == "05/2026"
    assert row["tenant_name"] == "Inquilino Rico"
    
    assert row["rent_amount"] == 2000.00
    assert row["agreement"] == 500.00
    assert row["commission_amount"] == 250.00
    assert row["net_income"] == 2250.00

def test_income_tax_analysis_empty_range(auth_client):
    response = auth_client.get("/analyses/income-tax?start_year=2024&start_month=1&end_year=2024&end_month=12")
    
    assert response.status_code == 200
    assert response.json() == []