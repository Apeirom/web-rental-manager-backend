def test_create_property(auth_client):
    payload = {
        "property_name": "Apt 101",
        "owner_name": "John Doe",
        "address": "123 Main St",
        "room_count": 2
    }
    response = auth_client.post("/properties", json=payload)
    
    assert response.status_code == 201
    assert response.json()["property_name"] == "Apt 101"
    assert "key" in response.json()
    assert "id" not in response.json()

def test_get_all_properties(auth_client):
    response = auth_client.get("/properties")
    
    assert response.status_code == 200
    res_json = response.json()
    assert "total" in res_json
    assert "skip" in res_json
    assert "limit" in res_json
    assert isinstance(res_json["data"], list)

def test_get_property_by_key(auth_client):
    payload = {
        "property_name": "Apt 102",
        "owner_name": "Jane Doe",
        "address": "456 Oak St",
        "room_count": 3
    }
    create_res = auth_client.post("/properties", json=payload)
    property_key = create_res.json()["key"]

    response = auth_client.get(f"/properties/{property_key}")
    assert response.status_code == 200
    assert response.json()["owner_name"] == "Jane Doe"

def test_get_property_not_found(auth_client):
    response = auth_client.get("/properties/invalid-uuid-key")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "RM-0003"

def test_update_property(auth_client):
    payload = {
        "property_name": "Apt 103",
        "owner_name": "Bob Smith",
        "address": "789 Pine St",
        "room_count": 1
    }
    create_res = auth_client.post("/properties", json=payload)
    property_key = create_res.json()["key"]

    update_payload = {
        "property_name": "Apt 103B",
        "owner_name": "Bob Smith Jr",
        "address": "789 Pine St",
        "room_count": 2
    }
    update_res = auth_client.put(f"/properties/{property_key}", json=update_payload)
    
    assert update_res.status_code == 200
    assert update_res.json()["property_name"] == "Apt 103B"
    assert update_res.json()["room_count"] == 2

def test_delete_property(auth_client):
    payload = {
        "property_name": "Apt 104",
        "owner_name": "Alice Brown",
        "address": "321 Elm St",
        "room_count": 4
    }
    create_res = auth_client.post("/properties", json=payload)
    property_key = create_res.json()["key"]

    delete_res = auth_client.delete(f"/properties/{property_key}")
    assert delete_res.status_code == 204

    get_res = auth_client.get(f"/properties/{property_key}")
    assert get_res.status_code == 404