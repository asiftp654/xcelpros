from pydantic import BaseModel, field_validator


class CalorieCounterBase(BaseModel):
    dish_name: str
    servings: int

    @field_validator("dish_name")
    def validate_dish_name(cls, value):
        if not value:
            raise ValueError("Dish name should not be empty")
        return value

    @field_validator("servings")
    def validate_servings(cls, value):
        if value < 1 or value > 1000:
            raise ValueError("Invalid Servings")
        return value


class CalorieCounterRequest(CalorieCounterBase):
    pass


class CalorieCounterResponse(CalorieCounterBase):
    calories_per_serving: float
    total_calories: float
    source: str = "USDA FoodData Central" 