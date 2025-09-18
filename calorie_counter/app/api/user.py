from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.schemas.user import SignUpRequest, LoginRequest
from app.crud.user import UserCrud
from app.models.user import User
from app.utils.user import UserService
from fastapi.responses import JSONResponse


user_router = APIRouter(prefix="/auth", tags=["auth"])


@user_router.post("/register")
async def user_registration(request: SignUpRequest, db: AsyncSession = Depends(get_async_db)):
    user_crud = UserCrud(db)
    user_service = UserService()    
    existing_user = await user_crud.get_by_email(request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    try:
        user = await user_crud.create_user(User(
            email=request.email,
            password=user_service.hash_password(request.password),
            first_name=request.first_name,
            last_name=request.last_name
        ))
        access_token = user_service.create_access_token(data={"sub": user.email, "user_id": user.id})
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "User created successfully", "access_token": access_token})

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )


@user_router.post("/login")
async def user_login(request: LoginRequest, db: AsyncSession = Depends(get_async_db)):
    user_crud = UserCrud(db)
    user_service = UserService()    
    user = await user_crud.get_by_email(request.email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid Credentials")

    if not user_service.verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid Credentials")

    access_token = user_service.create_access_token(data={"sub": user.email, "user_id": user.id})
    return JSONResponse(
        status_code=status.HTTP_200_OK, 
        content={"message": "Login successful", "access_token": access_token})