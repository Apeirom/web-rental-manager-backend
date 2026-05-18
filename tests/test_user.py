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