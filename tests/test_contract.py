def test_create_contract_success(client):
    tenant_res = client.post("/tenants", json={"name": "John Tenant", "document_number": "123.456.789-10"})
    tenant_key = tenant_res.json()["key"]

    prop_res = client.post("/properties", json={"property_name": "Apt 202", "owner_name": "Jane Owner", "address": "789 High St", "room_count": 3})
    property_key = prop_res.json()["key"]

    payload = {
        "guarantee": "deposit",
        "rental_deposit": 3000.00,
        "rent_amount": 1000.00,
        "room_name": "Suite A",
        "property_key": property_key,
        "tenant_key": tenant_key
    }
    response = client.post("/contracts", json=payload)
    
    assert response.status_code == 201
    assert response.json()["property"]["key"] == property_key
    assert response.json()["tenant"]["key"] == tenant_key
    assert "key" in response.json()

def test_create_contract_invalid_property(client):
    tenant_res = client.post("/tenants", json={"name": "Jane Tenant", "document_number": "987.654.321-00"})
    tenant_key = tenant_res.json()["key"]

    payload = {
        "guarantee": "deposit",
        "rental_deposit": 1500.00,
        "rent_amount": 500.00,
        "property_key": "non-existent-property-key",
        "tenant_key": tenant_key
    }
    response = client.post("/contracts", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0010"

def test_get_all_contracts(client):
    response = client.get("/contracts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_contract_by_key(client):
    tenant_res = client.post("/tenants", json={"name": "Alice Tenant", "document_number": "111.222.333-44"})
    tenant_key = tenant_res.json()["key"]

    prop_res = client.post("/properties", json={"property_name": "House 1", "owner_name": "Bob Owner", "address": "123 Green Rd", "room_count": 4})
    property_key = prop_res.json()["key"]

    payload = {
        "guarantee": "deposit",
        "rental_deposit": 2000.00,
        "rent_amount": 1000.00,
        "property_key": property_key,
        "tenant_key": tenant_key
    }
    create_res = client.post("/contracts", json=payload)
    contract_key = create_res.json()["key"]

    response = client.get(f"/contracts/{contract_key}")
    assert response.status_code == 200
    assert response.json()["rental_deposit"] == 2000.00

def test_update_contract(client):
    tenant_res = client.post("/tenants", json={"name": "Tenant One", "document_number": "222.333.444-55"})
    tenant_key = tenant_res.json()["key"]

    prop_res = client.post("/properties", json={"property_name": "Studio X", "owner_name": "Owner One", "address": "456 Central St", "room_count": 1})
    property_key = prop_res.json()["key"]

    payload = {
        "guarantee": "deposit",
        "rental_deposit": 1000.00,
        "rent_amount": 500.00,
        "property_key": property_key,
        "tenant_key": tenant_key
    }
    create_res = client.post("/contracts", json=payload)
    contract_key = create_res.json()["key"]

    update_payload = {
        "guarantee": "deposit",
        "rental_deposit": 1200.00,
        "rent_amount": 600.00,
        "property_key": property_key,
        "tenant_key": tenant_key,
        "acting": "active"
    }
    update_res = client.put(f"/contracts/{contract_key}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["rent_amount"] == 600.00

def test_delete_contract(client):
    tenant_res = client.post("/tenants", json={"name": "Tenant Two", "document_number": "888.777.666-55"})
    tenant_key = tenant_res.json()["key"]

    prop_res = client.post("/properties", json={"property_name": "Room 5", "owner_name": "Owner Two", "address": "789 Side St", "room_count": 1})
    property_key = prop_res.json()["key"]

    payload = {
        "guarantee": "deposit",
        "rental_deposit": 500.00,
        "rent_amount": 500.00,
        "property_key": property_key,
        "tenant_key": tenant_key
    }
    create_res = client.post("/contracts", json=payload)
    contract_key = create_res.json()["key"]

    delete_res = client.delete(f"/contracts/{contract_key}")
    assert delete_res.status_code == 204