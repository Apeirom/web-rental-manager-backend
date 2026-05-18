def test_create_real_estate(auth_client):
    payload = {
        "name": "Main Street Realty",
        "cnpj": "12.345.678/0001-00",
        "address": "789 Broker St",
        "commission": 6.5,
        "phone": "+5511999999999"
    }
    response = auth_client.post("/real-estates", json=payload)
    
    assert response.status_code == 201
    assert response.json()["name"] == "Main Street Realty"
    assert "key" in response.json()

def test_create_real_estate_invalid_cnpj(auth_client):
    payload = {
        "name": "Main Street Realty",
        "cnpj": "12345678000100",
        "address": "789 Broker St",
        "commission": 6.5,
        "phone": "+5511999999999"
    }
    response = auth_client.post("/real-estates", json=payload)
    assert response.status_code == 422

def test_create_real_estate_duplicate_cnpj(auth_client):
    payload = {
        "name": "Agency A",
        "cnpj": "11.222.333/0001-44",
        "address": "123 Alpha St",
        "commission": 5.0,
        "phone": "1234567"
    }
    auth_client.post("/real-estates", json=payload)
    response = auth_client.post("/real-estates", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0005"

def test_get_all_real_estates(auth_client):
    response = auth_client.get("/real-estates")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_real_estate_by_key(auth_client):
    payload = {
        "name": "Agency B",
        "cnpj": "55.666.777/0001-88",
        "address": "456 Beta St",
        "commission": 6.0,
        "phone": "7654321"
    }
    create_res = auth_client.post("/real-estates", json=payload)
    real_estate_key = create_res.json()["key"]

    response = auth_client.get(f"/real-estates/{real_estate_key}")
    assert response.status_code == 200
    assert response.json()["name"] == "Agency B"

def test_get_real_estate_not_found(auth_client):
    response = auth_client.get("/real-estates/non-existent-key")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "RM-0004"

def test_update_real_estate(auth_client):
    payload = {
        "name": "Agency C",
        "cnpj": "99.888.777/0001-11",
        "address": "789 Gamma St",
        "commission": 4.5,
        "phone": "999888777"
    }
    create_res = auth_client.post("/real-estates", json=payload)
    real_estate_key = create_res.json()["key"]

    update_payload = {
        "name": "Agency C Updated",
        "cnpj": "99.888.777/0001-11",
        "address": "789 Gamma St",
        "commission": 5.0,
        "phone": "999888777"
    }
    update_res = auth_client.put(f"/real-estates/{real_estate_key}", json=update_payload)
    
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Agency C Updated"
    assert update_res.json()["commission"] == 5.0

def test_delete_real_estate(auth_client):
    payload = {
        "name": "Agency D",
        "cnpj": "00.111.222/0001-33",
        "address": "101 Delta St",
        "commission": 7.0,
        "phone": "111222333"
    }
    create_res = auth_client.post("/real-estates", json=payload)
    real_estate_key = create_res.json()["key"]

    delete_res = auth_client.delete(f"/real-estates/{real_estate_key}")
    assert delete_res.status_code == 204

    get_res = auth_client.get(f"/real-estates/{real_estate_key}")
    assert get_res.status_code == 404