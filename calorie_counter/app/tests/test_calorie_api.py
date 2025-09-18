import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException


class TestCalorieCounter:

    @pytest_asyncio.fixture
    async def logged_in_user(self, client):
        user_data = {
            "email": "foodlover@test.com",
            "password": "password123",
            "first_name": "Food",
            "last_name": "Lover"
        }
        response = await client.post("/auth/register", json=user_data)
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_need_to_be_logged_in(self, client):
        food_request = {
            "dish_name": "pizza",
            "servings": 1
        }
        
        response = await client.post("/get-calories", json=food_request)
        assert response.status_code == 403
        
    @pytest.mark.asyncio
    @patch('app.api.calorie.RedisCache')
    @patch('app.api.calorie.USDAFoodService')
    async def test_handles_unknown_food_items(self, mock_usda, mock_cache, client, logged_in_user):
        cache_mock = MagicMock()
        cache_mock.get_cache.return_value = None
        mock_cache.return_value = cache_mock
        
        usda_mock = AsyncMock()
        usda_mock.get_best_match.side_effect = HTTPException(status_code=400, detail="Food not found")
        mock_usda.return_value = usda_mock
        
        weird_food = {
            "dish_name": "test12345",
            "servings": 1
        }
        
        response = await client.post("/get-calories", json=weird_food, headers=logged_in_user)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_dish_name_cannot_be_empty(self, client, logged_in_user):
        bad_request = {
            "dish_name": "",
            "servings": 1
        }
        
        response = await client.post("/get-calories", json=bad_request, headers=logged_in_user)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_servings_must_be_positive(self, client, logged_in_user):
        bad_request = {
            "dish_name": "pizza",
            "servings": 0
        }
        
        response = await client.post("/get-calories", json=bad_request, headers=logged_in_user)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_cannot_have_too_many_servings(self, client, logged_in_user):
        crazy_request = {
            "dish_name": "pizza",
            "servings": 9999
        }
        
        response = await client.post("/get-calories", json=crazy_request, headers=logged_in_user)
        assert response.status_code == 422
