import pytest

@pytest.fixture
def base_contract_key(client):
    tenant_res = client.post("/tenants", json={"name": "Extract Tenant", "document_number": "555.555.555-55"})
    tenant_key = tenant_res.json()["key"]

    prop_res = client.post("/properties", json={"property_name": "Extract Prop", "owner_name": "Owner", "address": "789 St", "room_count": 2})
    property_key = prop_res.json()["key"]

    contract_payload = {
        "guarantee": "deposit",
        "rental_deposit": 2000.00,
        "rent_amount": 1000.00,
        "property_key": property_key,
        "tenant_key": tenant_key
    }
    contract_res = client.post("/contracts", json=contract_payload)
    return contract_res.json()["key"]

def test_create_extract_success(client, base_contract_key):
    payload = {
        "month_ref": 1,
        "year_ref": 2027,
        "rent_amount": 1000.00,
        "iptu": 150.00,
        "water": 50.00,
        "agreement": 0.00,
        "contract_key": base_contract_key
    }
    response = client.post("/extracts", json=payload)
    
    assert response.status_code == 201
    assert response.json()["iptu"] == 150.00
    assert response.json()["contract"]["key"] == base_contract_key
    assert "key" in response.json()

def test_create_extract_invalid_contract(client):
    payload = {
        "month_ref": 2,
        "year_ref": 2027,
        "contract_key": "invalid-contract-key"
    }
    response = client.post("/extracts", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0014"

def test_get_extract_by_key(client, base_contract_key):
    payload = {
        "month_ref": 3,
        "year_ref": 2027,
        "rent_amount": 1000.00,
        "contract_key": base_contract_key
    }
    create_res = client.post("/extracts", json=payload)
    extract_key = create_res.json()["key"]

    response = client.get(f"/extracts/{extract_key}")
    assert response.status_code == 200
    assert response.json()["month_ref"] == 3
    assert response.json()["contract"]["rent_amount"] == 1000.00

def test_update_extract(client, base_contract_key):
    payload = {
        "month_ref": 4,
        "year_ref": 2027,
        "rent_amount": 1000.00,
        "contract_key": base_contract_key
    }
    create_res = client.post("/extracts", json=payload)
    extract_key = create_res.json()["key"]

    update_payload = {
        "month_ref": 4,
        "year_ref": 2027,
        "rent_amount": 1100.00,
        "iptu": 50.00,
        "water": 0.00,
        "agreement": 0.00,
        "contract_key": base_contract_key
    }
    update_res = client.put(f"/extracts/{extract_key}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["rent_amount"] == 1100.00
    assert update_res.json()["iptu"] == 50.00

def test_delete_extract(client, base_contract_key):
    payload = {
        "month_ref": 5,
        "year_ref": 2027,
        "contract_key": base_contract_key
    }
    create_res = client.post("/extracts", json=payload)
    extract_key = create_res.json()["key"]

    delete_res = client.delete(f"/extracts/{extract_key}")
    assert delete_res.status_code == 204