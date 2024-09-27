from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import JSON
from ..db import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    resume_url = Column(String)
    job_preferences = Column(JSON)
    hashed_password = Column(String)
