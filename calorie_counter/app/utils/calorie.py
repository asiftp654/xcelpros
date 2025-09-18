import json
import httpx
import numpy as np
from typing import List, Dict, Any
from fastapi import HTTPException
from app.core.config import settings
from app.core.database import redis_client


class USDAFoodService:
    
    def __init__(self, dish_name: str):
        self.dish_name = dish_name
        self.matcher = FoodMatcher()
    
    async def search_usda_api(self):
        try:
            query_params = {
                "query": self.dish_name,
                "api_key": settings.usda_api_key,
                "pageSize": settings.usda_page_size # Limiting only 5 best results from USDA API
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(settings.usda_api_url, params=query_params)
                
                if response.status_code == 429:
                    raise HTTPException(status_code=429, detail="Rate Limit Exceeded")
                
                response.raise_for_status()
                result = response.json()
                return result["foods"]
                
        except Exception as e:
            print(f"Error calling USDA API: {str(e)}")
            raise HTTPException(status_code=500, detail="USDA API Error")
    
    async def get_best_match(self):
        foods = await self.search_usda_api()
        if not foods:
            raise HTTPException(status_code=404, detail="Dish Not Found")

        best_match = self.matcher.find_best_match(self.dish_name, foods)
        return best_match


class FoodMatcher:
    
    def calculate_word_score(self, dish_name: str, description: str) -> float:
        dish_name_words = dish_name.lower().split()
        description_lower = description.lower()        
        matches = sum(1 for word in dish_name_words if word in description_lower)
        return matches / len(dish_name_words)
    
    def find_best_match(self, dish_name: str, foods: List[Any]):
        scores = np.array([
            self.calculate_word_score(dish_name, item["description"]) 
            for item in foods
        ])        
        best_score = np.max(scores)
        best_score_index = np.where(scores == best_score)[0]
        best_item = foods[best_score_index[0]]
        return best_item


class CalorieCounter:
    
    def __init__(self, food_item: Dict[str, Any]):
        self.food_item = food_item
        self.serving_size = 100
        self.serving_size_unit = "g"
        self.nutrient_id_dict = {1008: "Energy", 1003: "Protein", 1004: "Fat", 1005: "Carbohydrate"}
        self.calories_per_serving = self.get_calories_per_serving()
    
    def get_calories_per_serving(self) -> float:
        food_serving_size = self.get_food_serving_size() # we get the serving size in grams
        multiplication_factor = round(100 / food_serving_size, 2)
        food_nutrients = self.get_food_nutrients()
        calories = food_nutrients.get("Energy", 0.0)
        # If kcal data is found in the food_nutrients, then using it
        if calories:
            return round(calories * multiplication_factor, 2)
        
        protein = food_nutrients.get("Protein", 0.0) * 4
        carbohydrate = food_nutrients.get("Carbohydrate", 0.0) * 4
        fat = food_nutrients.get("Fat", 0.0) * 9
        
        total_calories = protein + carbohydrate + fat
        return round(total_calories * multiplication_factor, 2)        

    def get_food_serving_size(self) -> float:
        seriving_size = self.food_item.get('servingSize', 100)
        serving_unit = self.food_item.get('servingSizeUnit', 'g')
        if serving_unit == "g":
            return seriving_size
        elif serving_unit == "kg":
            return seriving_size * 1000
        return seriving_size # default to grams

    def get_food_nutrients(self) -> Dict[str, Any]:
        food_nutrients = {}
        for nutrient in self.food_item.get('foodNutrients', []):
            if nutrient.get("nutrientId") in self.nutrient_id_dict:
                food_nutrients[self.nutrient_id_dict[nutrient.get("nutrientId")]] = nutrient.get("value", 0.0)
        return food_nutrients


class RedisCache:
    def __init__(self):
        self.redis_client = redis_client

    def get_cache(self, key: str):
        cache = self.redis_client.get(key)
        return None if not cache else json.loads(cache)

    def set_cache(self, key: str, value: Any):
        self.redis_client.set(key, json.dumps(value))