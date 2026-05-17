def test_create_bail_insurance(client):
    payload = {
        "value": 1500.50,
        "validity": "2027-12-31",
        "insurance_company": "Safe Horizon Insurances"
    }
    response = client.post("/bail-insurances", json=payload)
    
    assert response.status_code == 201
    assert response.json()["insurance_company"] == "Safe Horizon Insurances"
    assert "key" in response.json()

def test_get_all_bail_insurances(client):
    response = client.get("/bail-insurances")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_bail_insurance_by_key(client):
    payload = {
        "value": 1200.00,
        "validity": "2026-08-30",
        "insurance_company": "Liberty Trust"
    }
    create_res = client.post("/bail-insurances", json=payload)
    bail_insurance_key = create_res.json()["key"]

    response = client.get(f"/bail-insurances/{bail_insurance_key}")
    assert response.status_code == 200
    assert response.json()["value"] == 1200.00

def test_get_bail_insurance_not_found(client):
    response = client.get("/bail-insurances/non-existent-key")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "RM-0008"

def test_update_bail_insurance(client):
    payload = {
        "value": 2000.00,
        "validity": "2027-01-01",
        "insurance_company": "Shield Corp"
    }
    create_res = client.post("/bail-insurances", json=payload)
    bail_insurance_key = create_res.json()["key"]

    update_payload = {
        "value": 2500.00,
        "validity": "2027-06-01",
        "insurance_company": "Shield Corp"
    }
    update_res = client.put(f"/bail-insurances/{bail_insurance_key}", json=update_payload)
    
    assert update_res.status_code == 200
    assert update_res.json()["value"] == 2500.00
    assert update_res.json()["validity"] == "2027-06-01"

def test_delete_bail_insurance(client):
    payload = {
        "value": 900.00,
        "validity": "2026-12-12",
        "insurance_company": "Alpha Guard"
    }
    create_res = client.post("/bail-insurances", json=payload)
    bail_insurance_key = create_res.json()["key"]

    delete_res = client.delete(f"/bail-insurances/{bail_insurance_key}")
    assert delete_res.status_code == 204

    get_res = client.get(f"/bail-insurances/{bail_insurance_key}")
    assert get_res.status_code == 404