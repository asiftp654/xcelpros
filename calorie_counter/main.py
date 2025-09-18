from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from app.api import user_router, calorie_router
from app.utils.user import format_error_response
from app.utils.calorie import RedisCache
from app.core.config import settings


app = FastAPI(
    title="Meal Calorie Counter"
)

app.include_router(user_router)
app.include_router(calorie_router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return format_error_response(exc.status_code, exc.detail)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    messages = [{err['loc'][-1]: err['msg']} for err in exc.errors()]
    return format_error_response(422, messages)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client = request.client.host
    key = f"rate_limit:{client}"
    cache = RedisCache()
    current_count = cache.redis_client.incr(key)

    if current_count == 1:
        cache.redis_client.expire(key, settings.rate_limit_time)

    if current_count > settings.rate_limit:
        ttl = cache.redis_client.ttl(key) 
        return format_error_response(
            status_code=429,
            message=f"Too many requests. Try again in {ttl} seconds."
        )

    response = await call_next(request)
    return response