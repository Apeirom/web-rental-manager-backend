def test_create_tenant(auth_client):
    payload = {
        "name": "Acme Corp",
        "document_number": "04.252.011/0001-10"
    }
    response = auth_client.post("/tenants", json=payload)
    
    assert response.status_code == 201
    assert response.json()["name"] == "Acme Corp"
    assert "key" in response.json()
    assert "id" not in response.json()

def test_create_tenant_normalizes_unformatted_document(auth_client):
    payload = {
        "name": "Acme Corp",
        "document_number": "52998224725"
    }
    response = auth_client.post("/tenants", json=payload)
    assert response.status_code == 201
    assert response.json()["document_number"] == "529.982.247-25"


def test_create_tenant_rejects_invalid_cpf(auth_client):
    response = auth_client.post(
        "/tenants",
        json={"name": "Invalid CPF", "document_number": "123.456.789-00"},
    )
    assert response.status_code == 422

def test_create_tenant_duplicate_document(auth_client):
    payload = {
        "name": "John Doe",
        "document_number": "529.982.247-25"
    }
    auth_client.post("/tenants", json=payload)
    response = auth_client.post("/tenants", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0002"

def test_get_all_tenants(auth_client):
    response = auth_client.get("/tenants")
    
    assert response.status_code == 200
    res_json = response.json()
    assert "total" in res_json
    assert "skip" in res_json
    assert "limit" in res_json
    assert isinstance(res_json["data"], list)

def test_get_tenant_by_key(auth_client):
    payload = {
        "name": "Jane Doe",
        "document_number": "111.444.777-35"
    }
    create_res = auth_client.post("/tenants", json=payload)
    tenant_key = create_res.json()["key"]

    response = auth_client.get(f"/tenants/{tenant_key}")
    assert response.status_code == 200
    assert response.json()["name"] == "Jane Doe"

def test_get_tenant_not_found(auth_client):
    response = auth_client.get("/tenants/invalid-uuid-key")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "RM-0001"

def test_update_tenant(auth_client):
    payload = {
        "name": "Bob Smith",
        "document_number": "100.000.000-19"
    }
    create_res = auth_client.post("/tenants", json=payload)
    tenant_key = create_res.json()["key"]

    update_payload = {
        "name": "Bob Smith Updated",
        "document_number": "100.000.000-19"
    }
    update_res = auth_client.put(f"/tenants/{tenant_key}", json=update_payload)
    
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Bob Smith Updated"

def test_delete_tenant(auth_client):
    payload = {
        "name": "Alice Brown",
        "document_number": "100.000.001-08"
    }
    create_res = auth_client.post("/tenants", json=payload)
    tenant_key = create_res.json()["key"]

    delete_res = auth_client.delete(f"/tenants/{tenant_key}")
    assert delete_res.status_code == 204

    get_res = auth_client.get(f"/tenants/{tenant_key}")
    assert get_res.status_code == 404