import jwt
from passlib.context import CryptContext
from fastapi.responses import JSONResponse
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import User
from app.core.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import UserCrud


class UserService:
    # User service for authentication and password management
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str):
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str):
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)    
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    def verify_token(self, token: str):
        try:
            return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        except jwt.PyJWTError:
            return None
    
    async def get_current_user(self, db: AsyncSession, token: str):
        try:
            payload = self.verify_token(token)
            if not payload:
                return None
            
            user_email = payload.get("sub")
            user_id = payload.get("user_id")        
            if not user_email or not user_id:
                return None
                
            user_crud = UserCrud(db)
            return await user_crud.get_by_email(user_email)
        except:
            return None


security = HTTPBearer()

# Dependency for authenticated apis
async def get_current_active_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                                db: AsyncSession = Depends(get_async_db)) -> User:
    user_service = UserService()
    token = credentials.credentials    
    user = await user_service.get_current_user(db, token)    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )    
    return user

def format_error_response(status_code: int, message: str):
    return JSONResponse(status_code=status_code, content={"code": status_code, "message": message})