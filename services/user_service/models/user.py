from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from services.database import Base
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserDB(Base):
    """SQLAlchemy User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    profile_picture = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Pydantic models for request/response
class UserBase(BaseModel):
    """Base user model with common attributes"""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="Username for login", min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., description="User's password", min_length=8)


class UserUpdate(BaseModel):
    """User update model with all fields optional"""
    email: Optional[EmailStr] = Field(None, description="User's email address")
    username: Optional[str] = Field(None, description="Username for login", min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    profile_picture: Optional[str] = Field(None, description="URL to profile picture")
    bio: Optional[str] = Field(None, description="Short biography", max_length=500)
    is_active: Optional[bool] = Field(None, description="Whether the user is active")
    is_premium: Optional[bool] = Field(None, description="Whether the user has premium account")


class User(UserBase):
    """User response model with all user data"""
    id: int
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    is_premium: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model used for JWT payload"""
    username: Optional[str] = None 