from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

# Enum for accepting and returning values
class EmploymentTypeFrontend(str, Enum):
    FullTime = "FullTime"
    PartTime = "PartTime"

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
    location_preference: Optional[str]
    keyword_preference: Optional[str]
    employment_type_preference: Optional[EmploymentTypeFrontend]
    notification_preference: bool

    class Config:
        from_attributes = True

# Schema for updating user details
class UserUpdate(BaseModel):
    resume_url: Optional[str] = None
    location_preference: Optional[str] = None
    keyword_preference: Optional[str] = None
    employment_type_preference: Optional[EmploymentTypeFrontend] = None
    notification_preference: Optional[bool] = None

# Schema for user login request
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
