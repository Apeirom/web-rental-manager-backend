import pytest


def test_create_property(auth_client, owner_factory):
    owner_key = owner_factory(name="John Doe")["key"]

    payload = {
        "property_name": "Apt 101",
        "equity_participations": [
            {"owner_key": owner_key, "participation_percentage": 100}
        ],
        "address": "123 Main St",
        "room_count": 2
    }
    response = auth_client.post("/properties", json=payload)
    
    assert response.status_code == 201
    assert response.json()["property_name"] == "Apt 101"
    assert "key" in response.json()
    assert "id" not in response.json()
    assert "owner" not in response.json()
    assert response.json()["equity_participations"] == [
        {
            "owner": {
                "key": owner_key,
                "name": "John Doe",
                "document_number": None,
            },
            "participation_percentage": 100,
        }
    ]

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
        "equity_participations": [
            {"owner_key": owner_key, "participation_percentage": 100}
        ],
        "address": "456 Oak St",
        "room_count": 3
    }
    create_res = auth_client.post("/properties", json=payload)
    property_key = create_res.json()["key"]

    response = auth_client.get(f"/properties/{property_key}")
    assert response.status_code == 200
    assert response.json()["property_name"] == "Apt 102"
    assert response.json()["equity_participations"][0]["owner"]["name"] == "Jane Doe"

def test_get_property_not_found(auth_client):
    response = auth_client.get("/properties/invalid-uuid-key")
    assert response.status_code == 404
    # Ajuste o código conforme o RM-0003 do seu PropertyNotFoundError
    assert response.json()["detail"]["code"] == "RM-0003" 

def test_update_property(auth_client, owner_factory):
    owner_key = owner_factory(name="Bob Smith")["key"]

    payload = {
        "property_name": "Apt 103",
        "equity_participations": [
            {"owner_key": owner_key, "participation_percentage": 100}
        ],
        "address": "789 Pine St",
        "room_count": 1
    }
    create_res = auth_client.post("/properties", json=payload)
    property_key = create_res.json()["key"]

    # Atualizando dados do imóvel
    update_payload = {
        "property_name": "Apt 103B",
        "equity_participations": [
            {"owner_key": owner_key, "participation_percentage": 100}
        ],
        "address": "789 Pine St",
        "room_count": 2
    }
    update_res = auth_client.put(f"/properties/{property_key}", json=update_payload)
    
    assert update_res.status_code == 200
    assert update_res.json()["property_name"] == "Apt 103B"
    assert update_res.json()["room_count"] == 2
    assert update_res.json()["equity_participations"][0]["owner"]["name"] == "Bob Smith"

def test_delete_property(auth_client, owner_factory):
    owner_key = owner_factory(name="Alice Brown")["key"]

    payload = {
        "property_name": "Apt 104",
        "equity_participations": [
            {"owner_key": owner_key, "participation_percentage": 100}
        ],
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


def test_property_rejects_participations_over_100_percent_with_custom_error(
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
    assert response.json()["detail"]["code"] == "RM-0031"


@pytest.mark.parametrize(
    "percentage",
    ["0", "-0.01", "100.01", "50.005"],
)
def test_property_rejects_invalid_individual_percentage_with_custom_error(
    auth_client,
    owner_factory,
    percentage,
):
    owner = owner_factory(name="Owner with invalid share")
    response = auth_client.post(
        "/properties",
        json={
            "property_name": "Invalid individual share",
            "equity_participations": [
                {
                    "owner_key": owner["key"],
                    "participation_percentage": percentage,
                }
            ],
            "address": "Rua D",
            "room_count": 1,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "RM-0030"


def test_property_creation_requires_at_least_one_equity_participation(
    auth_client,
):
    response = auth_client.post(
        "/properties",
        json={
            "property_name": "Without owners",
            "equity_participations": [],
            "address": "Rua E",
            "room_count": 1,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "RM-0029"


def test_property_update_allows_no_equity_participations(
    auth_client,
    property_factory,
):
    property_record = property_factory()

    response = auth_client.put(
        f"/properties/{property_record['key']}",
        json={
            "property_name": property_record["property_name"],
            "equity_participations": [],
            "address": property_record["address"],
            "room_count": property_record["room_count"],
        },
    )

    assert response.status_code == 200
    assert response.json()["equity_participations"] == []
    assert "owner" not in response.json()


def test_property_rejects_legacy_owner_key(auth_client, owner_factory):
    owner = owner_factory()
    response = auth_client.post(
        "/properties",
        json={
            "property_name": "Legacy owner contract",
            "owner_key": owner["key"],
            "address": "Rua F",
            "room_count": 1,
        },
    )

    assert response.status_code == 422


def test_property_rejects_duplicate_owner_participations(
    auth_client,
    owner_factory,
):
    owner = owner_factory()
    response = auth_client.post(
        "/properties",
        json={
            "property_name": "Repeated owner",
            "equity_participations": [
                {"owner_key": owner["key"], "participation_percentage": 40},
                {"owner_key": owner["key"], "participation_percentage": 40},
            ],
            "address": "Rua G",
            "room_count": 1,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "RM-0032"