from pydantic import BaseModel, EmailStr


# Schema for user creation (signup)
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


# Schema for returning user data (response model)
class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True  # Allows SQLAlchemy models to be returned as Pydantic models


# Schema for user login request
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
