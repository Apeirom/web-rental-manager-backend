def test_register_user_success(auth_client):
    payload = {
        "name": "Admin User",
        "email": "admin@company.com",
        "password": "strongpassword123"
    }
    response = auth_client.post("/users/register", json=payload)
    
    assert response.status_code == 201
    assert response.json()["name"] == "Admin User"
    assert response.json()["email"] == "admin@company.com"
    assert response.json()["role"] == "user"
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()

def test_register_duplicate_email(auth_client):
    payload = {
        "name": "Manager",
        "email": "manager@company.com",
        "password": "secure123"
    }
    auth_client.post("/users/register", json=payload)
    
    response = auth_client.post("/users/register", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0016"

def test_register_invalid_email_format(auth_client):
    payload = {
        "name": "Bad Email",
        "email": "not-an-email",
        "password": "pass"
    }
    response = auth_client.post("/users/register", json=payload)
    
    assert response.status_code == 422

def test_unauthorized_registration_attempt(client):
    payload = {
        "name": "Hacker",
        "email": "hacker@test.com",
        "password": "hack"
    }
    response = client.post("/users/register", json=payload)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing authorization header"


def test_update_my_profile(auth_client):
    payload = {
        "name": "Nome Atualizado",
        "email": "email.atualizado@test.com"
    }
    response = auth_client.put("/users/me", json=payload)
    
    assert response.status_code == 200
    assert response.json()["name"] == "Nome Atualizado"
    assert response.json()["email"] == "email.atualizado@test.com"

def test_list_paginated_users(auth_client):
    auth_client.post("/users/register", json={
        "name": "List User",
        "email": "list@company.com",
        "password": "pass"
    })

    response = auth_client.get("/users?skip=0&limit=5")
    
    assert response.status_code == 200
    assert "total" in response.json()
    assert isinstance(response.json()["data"], list)
    assert len(response.json()["data"]) >= 1

def test_update_user_role(auth_client):
    payload = {
        "name": "Role Test User",
        "email": "role@test.com",
        "password": "password123"
    }
    create_res = auth_client.post("/users/register", json=payload)
    user_key = create_res.json()["key"]

    role_payload = {"role": "manager"} 
    response = auth_client.patch(f"/users/{user_key}/role", json=role_payload)
    
    assert response.status_code == 200
    assert response.json()["role"] == "manager"