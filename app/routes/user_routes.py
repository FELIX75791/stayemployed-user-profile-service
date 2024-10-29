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

    # Convert the SQLAlchemy object to a Pydantic model
    user_response = UserResponse(
        user_id=new_user.user_id,
        name=new_user.name,
        email=new_user.email,
        resume_url=new_user.resume_url,
        job_preferences=new_user.job_preferences
    )

    # Create a Link header pointing to the login URL
    login_url = "/users/login"
    headers = {"Link": f"<{login_url}>; rel='next'"}

    return JSONResponse(content=user_response.dict(), headers=headers, status_code=201)


# Login route
@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate JWT token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/info/{user_email}", response_model=UserResponse)
def get_user_info(user_email: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Fetch user information
    user = get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the current user is allowed to access this information (optional)
    if current_user.user_email != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's information")

    return user


# Update user details
@router.put("/update/{user_id}", response_model=UserResponse)
def update_user_details(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db),
                        current_user: dict = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    return update_user(db, user_id, user_data)


# Delete user
@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    if not delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User successfully deleted"}
