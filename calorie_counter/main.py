from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from app.api.user import user_router
from app.utils.user import format_error_response


app = FastAPI(
    title="Meal Calorie Counter"
)

app.include_router(user_router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return format_error_response(exc.status_code, exc.detail)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    messages = [{err['loc'][-1]: err['msg']} for err in exc.errors()]
    return format_error_response(422, messages)