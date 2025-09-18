import pytest
import pytest_asyncio
from httpx import AsyncClient


class TestUserRegistration:

    @pytest.mark.asyncio
    async def test_can_register_new_user(self, client):
        user_info = {
            "email": "john.doe@gmail.com",
            "password": "mypassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        response = await client.post("/auth/register", json=user_info)
        assert response.status_code == 201
        result = response.json()
        assert result["message"] == "User created successfully"
        assert result["access_token"]

    @pytest.mark.asyncio
    async def test_cannot_register_with_same_email_twice(self, client):
        sarah_data = {
            "email": "sarah@example.com", 
            "password": "sarahpass123",
            "first_name": "Sarah",
            "last_name": "Connor"
        }
        
        first_attempt = await client.post("/auth/register", json=sarah_data)
        assert first_attempt.status_code == 201
        second_attempt = await client.post("/auth/register", json=sarah_data)
        assert second_attempt.status_code == 400
        error = second_attempt.json()
        assert "already" in error["message"].lower()

    @pytest.mark.asyncio
    async def test_password_too_short(self, client):
        weak_password_user = {
            "email": "weak@test.com",
            "password": "123",
            "first_name": "Weak", 
            "last_name": "Password"
        }
        
        response = await client.post("/auth/register", json=weak_password_user)
        assert response.status_code == 422


class TestUserLogin:

    @pytest_asyncio.fixture
    async def existing_user(self, client):
        user_data = {
            "email": "alice@wonderland.com",
            "password": "alicepassword123",
            "first_name": "Alice",
            "last_name": "Wonder"
        }
        
        await client.post("/auth/register", json=user_data)
        return user_data

    @pytest.mark.asyncio
    async def test_can_login_with_correct_credentials(self, client, existing_user):
        login_info = {
            "email": existing_user["email"],
            "password": existing_user["password"]
        }
        
        response = await client.post("/auth/login", json=login_info)        
        assert response.status_code == 200
        result = response.json()
        assert result["message"] == "Login successful"
        assert result["access_token"]  

    @pytest.mark.asyncio
    async def test_cannot_login_with_wrong_email(self, client):
        fake_login = {
            "email": "nobody@nowhere.com",
            "password": "somepassword123"
        }
        
        response = await client.post("/auth/login", json=fake_login)
        assert response.status_code == 400
        error = response.json()
        assert "Invalid Credentials" in error["message"]

    @pytest.mark.asyncio
    async def test_cannot_login_with_wrong_password(self, client, existing_user):
        wrong_password = {
            "email": existing_user["email"],
            "password": "wrongpassword"
        }
        
        response = await client.post("/auth/login", json=wrong_password)
        assert response.status_code == 400
        error = response.json()
        assert "Invalid Credentials" in error["message"]

