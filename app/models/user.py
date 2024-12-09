from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.mysql import JSON
from ..db import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(50), unique=True, index=True)
    resume_url = Column(String(100))
    job_preferences = Column(JSON)
    hashed_password = Column(String(255))
    notification_preference = Column(Boolean, default=True)
