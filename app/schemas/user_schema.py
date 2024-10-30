from pydantic import BaseModel, EmailStr
from typing import Optional, Dict


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
    resume_url: Optional[str]
    job_preferences: Optional[Dict]

    class Config:
        from_attributes = True


# Schema for user login request
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Schema for updating user details
class UserUpdate(BaseModel):
    resume_url: Optional[str] = None
    job_preferences: Optional[Dict] = None
