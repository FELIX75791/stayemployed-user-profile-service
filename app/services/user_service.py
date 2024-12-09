from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user_schema import UserCreate, UserUpdate
from ..services.auth_service import get_password_hash


# Create a new user
def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        notification_preference=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Get a user by email
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# Get a user by ID
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).first()


# Update user details
def update_user(db: Session, user_id: int, user_data: UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        if user_data.resume_url is not None:
            db_user.resume_url = user_data.resume_url
        if user_data.job_preferences is not None:
            db_user.job_preferences = user_data.job_preferences
        if user_data.notification_preference is not None:  # Add this logic
            db_user.notification_preference = user_data.notification_preference
        db.commit()
        db.refresh(db_user)
    return db_user


# Delete user
def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

def get_user_emails_with_notifications_enabled(db: Session):
    return db.query(User.email).filter(User.notification_preference == True).all()

