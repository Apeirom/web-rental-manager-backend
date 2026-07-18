import pytest

@pytest.fixture
def base_contract_key(auth_client):
    tenant_res = auth_client.post("/tenants", json={"name": "Payment Tenant", "document_number": "444.444.444-44"})
    prop_res = auth_client.post("/properties", json={"property_name": "Payment Prop", "owner_name": "Owner", "address": "789 St", "room_count": 2})
    
    contract_res = auth_client.post("/contracts", json={
        "guarantee_type": "deposit",
        "rental_deposit": 2000.00,
        "rent_amount": 1000.00,
        "property_key": prop_res.json()["key"],
        "tenant_key": tenant_res.json()["key"]
    })
    return contract_res.json()["key"]

def test_create_payment_success(auth_client):
    payload = {
        "payment_date": "2026-05-17",
        "amount": 1500.50
    }
    response = auth_client.post("/payments", json=payload)
    
    assert response.status_code == 201
    assert response.json()["amount"] == 1500.50
    assert response.json()["status"] == "unlinked"
    assert "key" in response.json()

def test_get_all_payments(auth_client):
    payload = {
        "payment_date": "2026-05-17",
        "amount": 1000.00
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

def test_get_all_payments_with_params(auth_client):
    auth_client.post("/payments", json={"payment_date": "2026-10-05", "amount": 3000.00})
    auth_client.post("/payments", json={"payment_date": "2026-10-15", "amount": 3000.00})
    auth_client.post("/payments", json={"payment_date": "2026-10-25", "amount": 4000.00})

    response = auth_client.get(
        "/payments?skip=0&limit=5&amount=3000.00&start_date=2026-10-01&end_date=2026-10-20&is_linked=false"
    )
    
    assert response.status_code == 200
    res_json = response.json()
    assert isinstance(res_json["data"], list)
    
    for payment in res_json["data"]:
        assert payment["amount"] == 3000.00
        assert payment["status"] == "unlinked"
        assert "2026-10-01" <= payment["payment_date"] <= "2026-10-20"

def test_get_payment_by_key(auth_client):
    payload = {
        "payment_date": "2026-07-17",
        "amount": 1200.00
    }
    create_res = auth_client.post("/payments", json=payload)
    payment_key = create_res.json()["key"]

    response = auth_client.get(f"/payments/{payment_key}")
    assert response.status_code == 200
    assert response.json()["amount"] == 1200.00

def test_update_payment_link_and_unlink(auth_client, base_contract_key):
    ext_res = auth_client.post("/extract-batches", json={
        "extracts": [{"month_ref": 1, "year_ref": 2026, "rent_amount": 1300.00, "contract_key": base_contract_key}]
    })
    batch_key = ext_res.json()["key"]

    pay_res = auth_client.post("/payments", json={"payment_date": "2026-01-10", "amount": 1300.00})
    payment_key = pay_res.json()["key"]

    link_res = auth_client.put(f"/payments/{payment_key}", json={
        "payment_date": "2026-01-10", 
        "amount": 1300.00, 
        "extract_batch_key": batch_key
    })
    assert link_res.status_code == 200
    assert link_res.json()["status"] == "linked"
    assert link_res.json()["extract_batch_key"] == batch_key

    unlink_res = auth_client.put(f"/payments/{payment_key}", json={
        "payment_date": "2026-01-10", 
        "amount": 1300.00, 
        "extract_batch_key": None
    })
    assert unlink_res.status_code == 200
    assert unlink_res.json()["status"] == "unlinked"
    assert unlink_res.json()["extract_batch_key"] is None

def test_delete_payment(auth_client):
    payload = {
        "payment_date": "2026-09-17",
        "amount": 1400.00
    }
    create_res = auth_client.post("/payments", json=payload)
    payment_key = create_res.json()["key"]

    delete_res = auth_client.delete(f"/payments/{payment_key}")
    assert delete_res.status_code == 204