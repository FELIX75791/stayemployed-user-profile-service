from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from typing import List

from ..models.user import EmploymentType
from ..schemas.user_schema import UserCreate, UserResponse, LoginRequest, UserUpdate
from ..services.user_service import create_user, get_user_by_email, update_user, delete_user, get_user_by_id, get_user_emails_with_notifications_enabled
from ..services.auth_service import verify_password, create_access_token, oauth2_scheme, decode_access_token
from ..dependencies import get_db, get_current_user

router = APIRouter()


# Signup route
@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = create_user(db, user)

    user_response = UserResponse(
        user_id=new_user.user_id,
        name=new_user.name,
        email=new_user.email,
        resume_url=new_user.resume_url,
        location_preference=new_user.location_preference,  # Will be None
        keyword_preference=new_user.keyword_preference,    # Will be None
        employment_type_preference=new_user.employment_type_preference,  # Will be None
        notification_preference=new_user.notification_preference
    )

    response_content = user_response.dict()
    response_content["links"] = [
        {"rel": "login", "href": "/login", "method": "POST"},
    ]

    return JSONResponse(content=response_content, status_code=201)


# Login route
@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate JWT token
    access_token = create_access_token(data={"sub": user.email})

    # Add HATEOAS links
    response_content = {
        "access_token": access_token,
        "token_type": "bearer",
        "links": [
            {"rel": "self", "href": "/login", "method": "POST"},
            {"rel": "info", "href": f"/info/{user.email}", "method": "GET"},
            {"rel": "update", "href": f"/update/{user.user_id}", "method": "PUT"},
            {"rel": "delete", "href": f"/delete/{user.user_id}", "method": "DELETE"},
        ]
    }
    return response_content


# Get user info
@router.get("/info/{user_email}", response_model=UserResponse)
def get_user_info(user_email: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user = get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.email != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's information")

    # Convert employment_type_preference to the response format
    if user.employment_type_preference == "Full Time":
        user.employment_type_preference = "FullTime"
    elif user.employment_type_preference == "Part Time":
        user.employment_type_preference = "PartTime"

    return UserResponse.model_validate(user)


# Update user details
@router.put("/update/{user_id}", response_model=UserResponse)
def update_user_details(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db),
                        current_user: dict = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    updated_user = update_user(db, user_id, user_data)

    # Convert employment_type_preference to string format
    if updated_user.employment_type_preference == EmploymentType.FullTime:
        updated_user.employment_type_preference = "FullTime"
    elif updated_user.employment_type_preference == EmploymentType.PartTime:
        updated_user.employment_type_preference = "PartTime"

    user_response = UserResponse.model_validate(updated_user)

    response_content = user_response.model_dump()
    response_content["links"] = [
        {"rel": "self", "href": f"/update/{user_id}", "method": "PUT"},
        {"rel": "info", "href": f"/info/{updated_user.email}", "method": "GET"},
        {"rel": "delete", "href": f"/delete/{user_id}", "method": "DELETE"},
    ]

    return JSONResponse(content=response_content)


# Delete user
@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    if not delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")

    # Add HATEOAS link to signup after deletion
    response_content = {
        "message": "User successfully deleted",
        "links": [
            {"rel": "signup", "href": "/signup", "method": "POST"}
        ]
    }

    return JSONResponse(content=response_content, status_code=status.HTTP_204_NO_CONTENT)

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Returns the current logged-in user's information.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not logged in. Please log in to access your profile.",
        )

    # Convert employment_type_preference to string
    if current_user.employment_type_preference == EmploymentType.FullTime:
        current_user.employment_type_preference = "FullTime"
    elif current_user.employment_type_preference == EmploymentType.PartTime:
        current_user.employment_type_preference = "PartTime"

    user_response = UserResponse.model_validate(current_user)

    response_content = user_response.model_dump()
    response_content["links"] = [
        {"rel": "self", "href": "/me", "method": "GET"},
        {"rel": "update", "href": f"/update/{current_user.user_id}", "method": "PUT"},
        {"rel": "delete", "href": f"/delete/{current_user.user_id}", "method": "DELETE"},
    ]

    return JSONResponse(content=response_content)


@router.get("/users/notifications-enabled", response_model=List[EmailStr])
def get_users_notifications_enabled(db: Session = Depends(get_db)):
    user_emails = get_user_emails_with_notifications_enabled(db)

    # Flatten the list of tuples into a plain list of emails
    return [email[0] for email in user_emails] if user_emails else []

@router.get("/preferences", response_model=dict)
def get_user_preferences(current_user: dict = Depends(get_current_user)):
    """
    Protected route to retrieve the user's preferences:
    employment_type_preference, location_preference, and keyword_preference.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not logged in. Please log in to access preferences.",
        )

    # Convert employment_type_preference to frontend-compatible format
    employment_type = None
    if current_user.employment_type_preference == EmploymentType.FullTime:
        employment_type = "Full Time"
    elif current_user.employment_type_preference == EmploymentType.PartTime:
        employment_type = "Part Time"

    preferences = {
        "employment_type_preference": employment_type,
        "location_preference": current_user.location_preference,
        "keyword_preference": current_user.keyword_preference,
    }

    return JSONResponse(content=preferences)



