def test_create_guarantor(auth_client):
    payload = {
        "type": "guarantor",
        "name": "Uncle Scrooge",
        "document_number": "123.456.789-10"
    }
    response = auth_client.post("/guarantees", json=payload)
    
    assert response.status_code == 201
    assert response.json()["type"] == "guarantor"
    assert response.json()["name"] == "Uncle Scrooge"
    assert "key" in response.json()

def test_create_bail_insurance(auth_client):
    payload = {
        "type": "bail_insurance",
        "value": 1500.50,
        "validity": "2027-12-31",
        "insurance_company": "Safe Horizon Insurances"
    }
    response = auth_client.post("/guarantees", json=payload)
    
    assert response.status_code == 201
    assert response.json()["type"] == "bail_insurance"
    assert response.json()["insurance_company"] == "Safe Horizon Insurances"
    assert "key" in response.json()

def test_create_deposit(auth_client):
    payload = {
        "type": "deposit",
        "amount": 3000.00,
        "paid_in_cash": True
    }
    response = auth_client.post("/guarantees", json=payload)
    
    assert response.status_code == 201
    assert response.json()["type"] == "deposit"
    assert response.json()["amount"] == 3000.00
    assert "key" in response.json()

def test_create_guarantee_invalid_type(auth_client):
    payload = {
        "type": "invalid_type",
        "amount": 3000.00
    }
    response = auth_client.post("/guarantees", json=payload)
    assert response.status_code == 422

def test_create_guarantor_duplicate_document(auth_client):
    payload = {
        "type": "guarantor",
        "name": "Guarantor X",
        "document_number": "987.654.321-00"
    }
    auth_client.post("/guarantees", json=payload)
    response = auth_client.post("/guarantees", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0007"

def test_get_all_guarantees(auth_client):
    auth_client.post("/guarantees", json={"type": "deposit", "amount": 1000})
    auth_client.post("/guarantees", json={"type": "guarantor", "name": "G", "document_number": "111.111.111-11"})

    response = auth_client.get("/guarantees")
    assert response.status_code == 200
    response_json = response.json()
    assert "total" in response_json
    assert response_json["total"] >= 2

    response_filtered = auth_client.get("/guarantees?guarantee_type=deposit")
    assert response_filtered.status_code == 200
    for item in response_filtered.json()["data"]:
        assert item["type"] == "deposit"

def test_update_guarantee(auth_client):
    payload = {
        "type": "deposit",
        "amount": 2000.00
    }
    create_response = auth_client.post("/guarantees", json=payload)
    guarantee_key = create_response.json()["key"]

    update_payload = {
        "type": "deposit",
        "amount": 2500.00,
        "paid_in_cash": False
    }
    update_response = auth_client.put(f"/guarantees/{guarantee_key}", json=update_payload)
    
    assert update_response.status_code == 200
    assert update_response.json()["amount"] == 2500.00
    assert update_response.json()["paid_in_cash"] is False

def test_delete_guarantee(auth_client):
    payload = {
        "type": "bail_insurance",
        "value": 900.00,
        "validity": "2026-12-12",
        "insurance_company": "Alpha Guard"
    }
    create_response = auth_client.post("/guarantees", json=payload)
    guarantee_key = create_response.json()["key"]

    delete_response = auth_client.delete(f"/guarantees/{guarantee_key}")
    assert delete_response.status_code == 204

    get_response = auth_client.get(f"/guarantees/{guarantee_key}")
    assert get_response.status_code == 404