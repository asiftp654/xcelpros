from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    def normalize_email(cls, value):
        return value.lower()

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class SignUpRequest(UserBase):
    first_name: str
    last_name: str

    @field_validator("first_name")
    def validate_first_name(cls, value):
        if len(value) < 1:
            raise ValueError("First Name Required") 
        return value

    @field_validator("last_name")
    def validate_last_name(cls, value):
        if len(value) < 1:
            raise ValueError("Last Name Required")
        return value


class LoginRequest(UserBase):
    pass