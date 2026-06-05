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
        "/payments?skip=0&limit=5&amount=3000.00&start_date=2026-10-01&end_date=2026-10-20&status=unlinked"
    )
    
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["skip"] == 0
    assert res_json["limit"] == 5
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

def test_update_payment(auth_client):
    payload = {
        "payment_date": "2026-08-17",
        "amount": 1300.00
    }
    create_res = auth_client.post("/payments", json=payload)
    payment_key = create_res.json()["key"]

    update_payload = {
        "payment_date": "2026-08-18",
        "amount": 1350.00,
        "status_enumerator": "linked"
    }
    update_res = auth_client.put(f"/payments/{payment_key}", json=update_payload)
    
    assert update_res.status_code == 200
    assert update_res.json()["payment_date"] == "2026-08-18"
    assert update_res.json()["amount"] == 1350.00
    assert update_res.json()["status"] == "linked"

def test_delete_payment(auth_client):
    payload = {
        "payment_date": "2026-09-17",
        "amount": 1400.00
    }
    create_res = auth_client.post("/payments", json=payload)
    payment_key = create_res.json()["key"]

    delete_res = auth_client.delete(f"/payments/{payment_key}")
    assert delete_res.status_code == 204