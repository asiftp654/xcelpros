from fastapi import APIRouter
from app.schemas.calorie import CalorieCounterRequest, CalorieCounterResponse
from app.models.user import User
from app.utils.user import get_current_active_user
from fastapi import Depends
from app.utils.calorie import USDAFoodService, CalorieCounter, RedisCache


calorie_router = APIRouter(prefix="", tags=["calorie"])


@calorie_router.post("/get-calories")
async def get_calories(request: CalorieCounterRequest, user: User = Depends(get_current_active_user)):
    # Checking if the dish name is in the cache
    cache = RedisCache()
    cached_value = cache.get_cache(request.dish_name)
    if cached_value:
        description = cached_value["description"]
        calories_per_serving = cached_value["calories_per_serving"]
        calories_per_serving = float(calories_per_serving)
        total_calories = round(calories_per_serving * request.servings, 2)
        return CalorieCounterResponse(
            dish_name=description,
            servings=request.servings,
            calories_per_serving=calories_per_serving,
            total_calories=total_calories
        )

    # Getting the best matched food from the USDA FoodData Central
    service = USDAFoodService(dish_name=request.dish_name)
    best_matched_food = await service.get_best_match()

    # Calculating the calories per serving
    calorie_counter = CalorieCounter(best_matched_food)
    calories_per_serving = calorie_counter.get_calories_per_serving()
    cache_value = {"description": best_matched_food["description"], "calories_per_serving": calories_per_serving}
    cache.set_cache(request.dish_name, cache_value)

    total_calories = round(calories_per_serving * request.servings, 2)
    return CalorieCounterResponse(
        dish_name=best_matched_food["description"],
        servings=request.servings,
        calories_per_serving=calories_per_serving,
        total_calories=total_calories
    )