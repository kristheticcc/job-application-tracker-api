# Imports
from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True)
    hashed_password = Column(String)
    full_name = Column(String)
    email = Column(String, unique=True)
    age = Column(Integer)

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key = True)
    company = Column(String)
    role = Column(String)
    location = Column(String)
    status = Column(String, default="APPLIED")
    user_id = Column(Integer, ForeignKey("users.id"))
