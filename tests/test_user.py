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

def test_list_paginated_users_ordered_by_created_at_desc(auth_client):
    user_one = auth_client.post(
        "/users/register",
        json={
            "name": "User Order One",
            "email": "user_order_one@test.com",
            "password": "password123",
        },
    ).json()

    user_two = auth_client.post(
        "/users/register",
        json={
            "name": "User Order Two",
            "email": "user_order_two@test.com",
            "password": "password123",
        },
    ).json()

    response = auth_client.get("/users?limit=10")
    assert response.status_code == 200
    user_keys = [item["key"] for item in response.json()["data"]]
    assert user_keys.index(user_two["key"]) < user_keys.index(user_one["key"])

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


def test_update_password_requires_current_password(auth_client):
    payload = {
        "password": "brandnewpassword123"
    }
    response = auth_client.put("/users/me", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0037"


def test_update_password_wrong_current_password(auth_client):
    payload = {
        "current_password": "wrongpassword",
        "password": "brandnewpassword123"
    }
    response = auth_client.put("/users/me", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0038"


def test_admin_reset_password_success(auth_client, client):
    create_payload = {
        "name": "User To Reset",
        "email": "reset.me@test.com",
        "password": "oldpassword123"
    }
    create_res = auth_client.post("/users/register", json=create_payload)
    user_key = create_res.json()["key"]

    reset_payload = {"new_password": "newtemporarysecret999"}
    reset_res = auth_client.post(f"/users/{user_key}/reset-password", json=reset_payload)
    assert reset_res.status_code == 200

    login_res = client.post("/auth/login", json={"email": "reset.me@test.com", "password": "newtemporarysecret999"})
    assert login_res.status_code == 200
    assert "token" in login_res.json()


def test_admin_reset_password_forbidden_for_non_master(non_master_client):
    reset_payload = {"new_password": "maliciousresetpassword"}
    reset_res = non_master_client.post("/users/target-user-key/reset-password", json=reset_payload)
    assert reset_res.status_code == 403
    assert reset_res.json()["detail"]["code"] == "RM-0020"