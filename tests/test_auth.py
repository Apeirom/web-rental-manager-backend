def test_login_success(client, auth_client):
    payload = {
        "name": "Login Test",
        "email": "login@test.com",
        "password": "correcthorsebatterystaple"
    }
    auth_client.post("/users/register", json=payload)

    login_payload = {
        "email": "login@test.com",
        "password": "correcthorsebatterystaple"
    }
    response = client.post("/auth/login", json=login_payload)
    
    assert response.status_code == 200
    assert "token" in response.json()
    assert "access_token" in response.json()["token"]
    assert response.json()["token"]["token_type"] == "bearer"

def test_login_invalid_password(client, auth_client):
    payload = {
        "name": "Wrong Pass",
        "email": "wrongpass@test.com",
        "password": "realpassword"
    }
    auth_client.post("/users/register", json=payload)

    login_payload = {
        "email": "wrongpass@test.com",
        "password": "fakepassword"
    }
    response = client.post("/auth/login", json=login_payload)
    
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "RM-0017"

def test_login_non_existent_user(client):
    login_payload = {
        "email": "ghost@test.com",
        "password": "password123"
    }
    response = client.post("/auth/login", json=login_payload)
    
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "RM-0017"

def test_access_protected_route_without_token(client):
    response = client.get("/tenants")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing authorization header"

def test_access_protected_route_with_invalid_token(client):
    client.headers.update({"Authorization": "Bearer invalid.fake.token"})
    response = client.get("/tenants")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"