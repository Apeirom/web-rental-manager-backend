def test_create_tenant(client):
    payload = {
        "name": "Acme Corp",
        "document_number": "12.345.678/0001-99"
    }
    response = client.post("/tenants", json=payload)
    
    assert response.status_code == 201
    assert response.json()["name"] == "Acme Corp"
    assert "key" in response.json()
    assert "id" not in response.json()

def test_create_tenant_invalid_document_format(client):
    payload = {
        "name": "Acme Corp",
        "document_number": "12345678900" 
    }
    response = client.post("/tenants", json=payload)
    assert response.status_code == 422

def test_create_tenant_duplicate_document(client):
    payload = {
        "name": "John Doe",
        "document_number": "123.456.789-00"
    }
    client.post("/tenants", json=payload)
    response = client.post("/tenants", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0002"

def test_get_all_tenants(client):
    response = client.get("/tenants")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_tenant_by_key(client):
    payload = {
        "name": "Jane Doe",
        "document_number": "987.654.321-11"
    }
    create_res = client.post("/tenants", json=payload)
    tenant_key = create_res.json()["key"]

    response = client.get(f"/tenants/{tenant_key}")
    assert response.status_code == 200
    assert response.json()["name"] == "Jane Doe"

def test_get_tenant_not_found(client):
    response = client.get("/tenants/invalid-uuid-key")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "RM-0001"

def test_update_tenant(client):
    payload = {
        "name": "Bob Smith",
        "document_number": "111.222.333-44"
    }
    create_res = client.post("/tenants", json=payload)
    tenant_key = create_res.json()["key"]

    update_payload = {
        "name": "Bob Smith Updated",
        "document_number": "111.222.333-44"
    }
    update_res = client.put(f"/tenants/{tenant_key}", json=update_payload)
    
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Bob Smith Updated"

def test_delete_tenant(client):
    payload = {
        "name": "Alice Brown",
        "document_number": "555.666.777-88"
    }
    create_res = client.post("/tenants", json=payload)
    tenant_key = create_res.json()["key"]

    delete_res = client.delete(f"/tenants/{tenant_key}")
    assert delete_res.status_code == 204

    get_res = client.get(f"/tenants/{tenant_key}")
    assert get_res.status_code == 404