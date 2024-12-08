from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from ..schemas.user_schema import UserCreate, UserResponse, LoginRequest, UserUpdate
from ..services.user_service import create_user, get_user_by_email, update_user, delete_user, get_user_by_id
from ..services.auth_service import verify_password, create_access_token, oauth2_scheme, decode_access_token
from ..dependencies import get_db, get_current_user
from jose import JWTError

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
        job_preferences=new_user.job_preferences
    )

    # Add HATEOAS links
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

    user_response = UserResponse.model_validate(user)

    # Add HATEOAS links
    response_content = user_response.model_dump()
    response_content["links"] = [
        {"rel": "self", "href": f"/info/{user_email}", "method": "GET"},
        {"rel": "update", "href": f"/update/{user.user_id}", "method": "PUT"},
        {"rel": "delete", "href": f"/delete/{user.user_id}", "method": "DELETE"},
    ]

    return JSONResponse(content=response_content)


# Update user details
@router.put("/update/{user_id}", response_model=UserResponse)
def update_user_details(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db),
                        current_user: dict = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    updated_user = update_user(db, user_id, user_data)

    user_response = UserResponse.model_validate(updated_user)

    # Add HATEOAS links
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

    user_response = UserResponse.model_validate(current_user)

    response_content = user_response.model_dump()
    response_content["links"] = [
        {"rel": "self", "href": "/me", "method": "GET"},
        {"rel": "update", "href": f"/update/{current_user.user_id}", "method": "PUT"},
        {"rel": "delete", "href": f"/delete/{current_user.user_id}", "method": "DELETE"},
    ]

    return JSONResponse(content=response_content)
