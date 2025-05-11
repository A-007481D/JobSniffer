from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from services.database import Base
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class JobSourceDB(Base):
    """SQLAlchemy JobSource model"""
    __tablename__ = "job_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class JobDB(Base):
    """SQLAlchemy Job model"""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String, index=True)
    description = Column(Text)
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String)
    job_type = Column(String)  # full-time, part-time, contract, etc.
    remote = Column(Boolean, default=False)
    url = Column(String)
    source_id = Column(Integer, ForeignKey("job_sources.id"))
    external_id = Column(String)  # ID from the source
    parsed_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    source = relationship("JobSourceDB")


class JobAlertDB(Base):
    """SQLAlchemy JobAlert model"""
    __tablename__ = "job_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    keywords = Column(String)
    locations = Column(String)
    job_types = Column(String)
    remote = Column(Boolean)
    salary_min = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship("UserDB")


# Pydantic models for request/response
class JobSourceBase(BaseModel):
    name: str
    url: str
    is_active: bool = True


class JobSourceCreate(JobSourceBase):
    pass


class JobSource(JobSourceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class JobBase(BaseModel):
    title: str
    company: str
    location: str
    description: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    job_type: Optional[str] = None
    remote: bool = False
    url: str
    source_id: int
    external_id: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None


class JobCreate(JobBase):
    pass


class Job(JobBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    source: Optional[JobSource] = None

    class Config:
        orm_mode = True


class JobAlertBase(BaseModel):
    title: str
    keywords: str
    locations: Optional[str] = None
    job_types: Optional[str] = None
    remote: Optional[bool] = None
    salary_min: Optional[float] = None
    is_active: bool = True


class JobAlertCreate(JobAlertBase):
    pass


class JobAlertUpdate(BaseModel):
    title: Optional[str] = None
    keywords: Optional[str] = None
    locations: Optional[str] = None
    job_types: Optional[str] = None
    remote: Optional[bool] = None
    salary_min: Optional[float] = None
    is_active: Optional[bool] = None


class JobAlert(JobAlertBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True 