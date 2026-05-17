import pytest

@pytest.fixture
def base_contract_key(client):
    tenant_res = client.post("/tenants", json={"name": "Payment Tenant", "document_number": "111.111.111-11"})
    tenant_key = tenant_res.json()["key"]

    prop_res = client.post("/properties", json={"property_name": "Payment Prop", "owner_name": "Owner", "address": "123 St", "room_count": 2})
    property_key = prop_res.json()["key"]

    contract_payload = {
        "guarantee": "deposit",
        "rental_deposit": 1000.00,
        "rent_amount": 1000.00,
        "property_key": property_key,
        "tenant_key": tenant_key
    }
    contract_res = client.post("/contracts", json=contract_payload)
    return contract_res.json()["key"]

def test_create_payment_success(client, base_contract_key):
    payload = {
        "payment_date": "2026-05-17",
        "month_ref": 5,
        "year_ref": 2026,
        "contract_key": base_contract_key
    }
    response = client.post("/payments", json=payload)
    
    assert response.status_code == 201
    assert response.json()["month_ref"] == 5
    assert response.json()["contract"]["key"] == base_contract_key
    assert "key" in response.json()

def test_create_payment_invalid_contract(client):
    payload = {
        "payment_date": "2026-06-17",
        "month_ref": 6,
        "year_ref": 2026,
        "contract_key": "invalid-contract-key"
    }
    response = client.post("/payments", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0012"

def test_get_payment_by_key(client, base_contract_key):
    payload = {
        "payment_date": "2026-07-17",
        "month_ref": 7,
        "year_ref": 2026,
        "contract_key": base_contract_key
    }
    create_res = client.post("/payments", json=payload)
    payment_key = create_res.json()["key"]

    response = client.get(f"/payments/{payment_key}")
    assert response.status_code == 200
    assert response.json()["month_ref"] == 7
    assert response.json()["contract"]["rent_amount"] == 1000.00

def test_update_payment(client, base_contract_key):
    payload = {
        "payment_date": "2026-08-17",
        "month_ref": 8,
        "year_ref": 2026,
        "contract_key": base_contract_key
    }
    create_res = client.post("/payments", json=payload)
    payment_key = create_res.json()["key"]

    update_payload = {
        "payment_date": "2026-08-18",
        "month_ref": 8,
        "year_ref": 2026,
        "contract_key": base_contract_key
    }
    update_res = client.put(f"/payments/{payment_key}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["payment_date"] == "2026-08-18"

def test_delete_payment(client, base_contract_key):
    payload = {
        "payment_date": "2026-09-17",
        "month_ref": 9,
        "year_ref": 2026,
        "contract_key": base_contract_key
    }
    create_res = client.post("/payments", json=payload)
    payment_key = create_res.json()["key"]

    delete_res = client.delete(f"/payments/{payment_key}")
    assert delete_res.status_code == 204