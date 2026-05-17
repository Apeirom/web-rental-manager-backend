def test_create_guarantor(client):
    payload = {
        "name": "Uncle Scrooge",
        "document_number": "123.456.789-10"
    }
    response = client.post("/guarantors", json=payload)
    
    assert response.status_code == 201
    assert response.json()["name"] == "Uncle Scrooge"
    assert "key" in response.json()

def test_create_guarantor_invalid_document(client):
    payload = {
        "name": "Uncle Scrooge",
        "document_number": "12345678910"
    }
    response = client.post("/guarantors", json=payload)
    assert response.status_code == 422

def test_create_guarantor_duplicate_document(client):
    payload = {
        "name": "Guarantor X",
        "document_number": "987.654.321-00"
    }
    client.post("/guarantors", json=payload)
    response = client.post("/guarantors", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0007"

def test_get_all_guarantors(client):
    response = client.get("/guarantors")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_guarantor_by_key(client):
    payload = {
        "name": "Guarantor Y",
        "document_number": "555.444.333-22"
    }
    create_res = client.post("/guarantors", json=payload)
    guarantor_key = create_res.json()["key"]

    response = client.get(f"/guarantors/{guarantor_key}")
    assert response.status_code == 200
    assert response.json()["name"] == "Guarantor Y"

def test_get_guarantor_not_found(client):
    response = client.get("/guarantors/non-existent-key")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "RM-0006"

def test_update_guarantor(client):
    payload = {
        "name": "Guarantor Z",
        "document_number": "111.222.333-44"
    }
    create_res = client.post("/guarantors", json=payload)
    guarantor_key = create_res.json()["key"]

    update_payload = {
        "name": "Guarantor Z Updated",
        "document_number": "111.222.333-44"
    }
    update_res = client.put(f"/guarantors/{guarantor_key}", json=update_payload)
    
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Guarantor Z Updated"

def test_delete_guarantor(client):
    payload = {
        "name": "Guarantor W",
        "document_number": "777.888.999-00"
    }
    create_res = client.post("/guarantors", json=payload)
    guarantor_key = create_res.json()["key"]

    delete_res = client.delete(f"/guarantors/{guarantor_key}")
    assert delete_res.status_code == 204

    get_res = client.get(f"/guarantors/{guarantor_key}")
    assert get_res.status_code == 404