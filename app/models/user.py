from sqlalchemy import Column, Integer, String, Boolean, Enum
from ..db import Base
import enum

class EmploymentType(enum.Enum):
    FullTime = "Full Time"
    PartTime = "Part Time"

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(50), unique=True, index=True)
    resume_url = Column(String(100))
    location_preference = Column(String(255), nullable=True)
    keyword_preference = Column(String(255), nullable=True)
    employment_type_preference = Column(Enum(EmploymentType), nullable=True)
    hashed_password = Column(String(255))
    notification_preference = Column(Boolean, default=True)
