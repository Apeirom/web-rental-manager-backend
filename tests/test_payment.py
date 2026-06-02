import pytest

@pytest.fixture
def base_contract_key(auth_client):
    tenant_res = auth_client.post("/tenants", json={"name": "Payment Tenant", "document_number": "111.111.111-11"})
    tenant_key = tenant_res.json()["key"]

    prop_res = auth_client.post("/properties", json={"property_name": "Payment Prop", "owner_name": "Owner", "address": "123 St", "room_count": 2})
    property_key = prop_res.json()["key"]

    contract_payload = {
        "guarantee_type": "deposit",
        "rental_deposit": 1000.00,
        "rent_amount": 1000.00,
        "property_key": property_key,
        "tenant_key": tenant_key
    }
    contract_res = auth_client.post("/contracts", json=contract_payload)
    return contract_res.json()["key"]

def test_create_payment_success(auth_client, base_contract_key):
    payload = {
        "payment_date": "2026-05-17",
        "month_ref": 5,
        "year_ref": 2026,
        "contract_key": base_contract_key
    }
    response = auth_client.post("/payments", json=payload)
    
    assert response.status_code == 201
    assert response.json()["month_ref"] == 5
    assert response.json()["contract"]["key"] == base_contract_key
    assert "key" in response.json()

def test_create_payment_invalid_contract(auth_client):
    payload = {
        "payment_date": "2026-06-17",
        "month_ref": 6,
        "year_ref": 2026,
        "contract_key": "invalid-contract-key"
    }
    response = auth_client.post("/payments", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0012"

def test_get_all_payments(auth_client, base_contract_key):
    payload = {
        "payment_date": "2026-05-17",
        "month_ref": 5,
        "year_ref": 2026,
        "contract_key": base_contract_key
    }
    auth_client.post("/payments", json=payload)

    response = auth_client.get("/payments")
    assert response.status_code == 200
    res_json = response.json()
    assert "total" in res_json
    assert "skip" in res_json
    assert "limit" in res_json
    assert isinstance(res_json["data"], list)
    assert len(res_json["data"]) >= 1

def test_get_all_payments_with_params(auth_client, base_contract_key):
    response = auth_client.get("/payments?skip=0&limit=5&only_active_contracts=true")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["skip"] == 0
    assert res_json["limit"] == 5
    assert isinstance(res_json["data"], list)

def test_get_payment_by_key(auth_client, base_contract_key):
    payload = {
        "payment_date": "2026-07-17",
        "month_ref": 7,
        "year_ref": 2026,
        "contract_key": base_contract_key
    }
    create_res = auth_client.post("/payments", json=payload)
    payment_key = create_res.json()["key"]

    response = auth_client.get(f"/payments/{payment_key}")
    assert response.status_code == 200
    assert response.json()["month_ref"] == 7
    assert response.json()["contract"]["rent_amount"] == 1000.00

def test_update_payment(auth_client, base_contract_key):
    payload = {
        "payment_date": "2026-08-17",
        "month_ref": 8,
        "year_ref": 2026,
        "contract_key": base_contract_key
    }
    create_res = auth_client.post("/payments", json=payload)
    payment_key = create_res.json()["key"]

    update_payload = {
        "payment_date": "2026-08-18",
        "month_ref": 8,
        "year_ref": 2026,
        "contract_key": base_contract_key
    }
    update_res = auth_client.put(f"/payments/{payment_key}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["payment_date"] == "2026-08-18"

def test_delete_payment(auth_client, base_contract_key):
    payload = {
        "payment_date": "2026-09-17",
        "month_ref": 9,
        "year_ref": 2026,
        "contract_key": base_contract_key
    }
    create_res = auth_client.post("/payments", json=payload)
    payment_key = create_res.json()["key"]

    delete_res = auth_client.delete(f"/payments/{payment_key}")
    assert delete_res.status_code == 204