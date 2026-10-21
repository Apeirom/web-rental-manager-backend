def test_create_property(auth_client, owner_factory):
    owner_key = owner_factory(name="John Doe")["key"]

    payload = {
        "property_name": "Apt 101",
        "owner_key": owner_key,
        "address": "123 Main St",
        "room_count": 2
    }
    response = auth_client.post("/properties", json=payload)
    
    assert response.status_code == 201
    assert response.json()["property_name"] == "Apt 101"
    assert "key" in response.json()
    assert "id" not in response.json()
    # 3. Verifica se o DTO aninhado de owner retornou corretamente
    assert response.json()["owner"]["name"] == "John Doe"
    assert response.json()["owner"]["key"] == owner_key

def test_get_all_properties(auth_client):
    response = auth_client.get("/properties")
    
    assert response.status_code == 200
    res_json = response.json()
    assert "total" in res_json
    assert "skip" in res_json
    assert "limit" in res_json
    assert isinstance(res_json["data"], list)

def test_get_property_by_key(auth_client, owner_factory):
    owner_key = owner_factory(name="Jane Doe")["key"]

    payload = {
        "property_name": "Apt 102",
        "owner_key": owner_key,
        "address": "456 Oak St",
        "room_count": 3
    }
    create_res = auth_client.post("/properties", json=payload)
    property_key = create_res.json()["key"]

    response = auth_client.get(f"/properties/{property_key}")
    assert response.status_code == 200
    assert response.json()["property_name"] == "Apt 102"
    assert response.json()["owner"]["name"] == "Jane Doe"

def test_get_property_not_found(auth_client):
    response = auth_client.get("/properties/invalid-uuid-key")
    assert response.status_code == 404
    # Ajuste o código conforme o RM-0003 do seu PropertyNotFoundError
    assert response.json()["detail"]["code"] == "RM-0003" 

def test_update_property(auth_client, owner_factory):
    owner_key = owner_factory(name="Bob Smith")["key"]

    payload = {
        "property_name": "Apt 103",
        "owner_key": owner_key,
        "address": "789 Pine St",
        "room_count": 1
    }
    create_res = auth_client.post("/properties", json=payload)
    property_key = create_res.json()["key"]

    # Atualizando dados do imóvel
    update_payload = {
        "property_name": "Apt 103B",
        "owner_key": owner_key, # Mantendo o mesmo dono
        "address": "789 Pine St",
        "room_count": 2
    }
    update_res = auth_client.put(f"/properties/{property_key}", json=update_payload)
    
    assert update_res.status_code == 200
    assert update_res.json()["property_name"] == "Apt 103B"
    assert update_res.json()["room_count"] == 2
    assert update_res.json()["owner"]["name"] == "Bob Smith"

def test_delete_property(auth_client, owner_factory):
    owner_key = owner_factory(name="Alice Brown")["key"]

    payload = {
        "property_name": "Apt 104",
        "owner_key": owner_key,
        "address": "321 Elm St",
        "room_count": 4
    }
    create_res = auth_client.post("/properties", json=payload)
    property_key = create_res.json()["key"]

    delete_res = auth_client.delete(f"/properties/{property_key}")
    assert delete_res.status_code == 204

    get_res = auth_client.get(f"/properties/{property_key}")
    assert get_res.status_code == 404


def test_property_supports_owner_specific_equity_participations(
    auth_client, owner_factory
):
    owner_x = owner_factory(name="Owner X")
    owner_y = owner_factory(name="Owner Y")

    first = auth_client.post(
        "/properties",
        json={
            "property_name": "Imóvel A",
            "equity_participations": [
                {
                    "owner_key": owner_x["key"],
                    "participation_percentage": 100,
                }
            ],
            "address": "Rua A",
            "room_count": 1,
        },
    )
    second = auth_client.post(
        "/properties",
        json={
            "property_name": "Imóvel B",
            "equity_participations": [
                {
                    "owner_key": owner_x["key"],
                    "participation_percentage": 50,
                },
                {
                    "owner_key": owner_y["key"],
                    "participation_percentage": 25,
                },
            ],
            "address": "Rua B",
            "room_count": 2,
        },
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["equity_participations"][0]["owner"]["key"] == owner_x["key"]
    assert first.json()["equity_participations"][0]["participation_percentage"] == 100
    second_shares = {
        row["owner"]["key"]: row["participation_percentage"]
        for row in second.json()["equity_participations"]
    }
    assert second_shares == {owner_x["key"]: 50, owner_y["key"]: 25}


def test_property_rejects_participations_over_100_percent(
    auth_client, owner_factory
):
    owner_x = owner_factory(name="Owner X")
    owner_y = owner_factory(name="Owner Y")
    response = auth_client.post(
        "/properties",
        json={
            "property_name": "Invalid shares",
            "equity_participations": [
                {"owner_key": owner_x["key"], "participation_percentage": 60},
                {"owner_key": owner_y["key"], "participation_percentage": 50},
            ],
            "address": "Rua C",
            "room_count": 1,
        },
    )

    assert response.status_code == 422