from sqlalchemy import Column, Integer, String
from database import Base

# User table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    role = Column(String(100), nullable=False, index=True)