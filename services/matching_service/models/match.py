from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from services.database import Base
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class MatchDB(Base):
    """SQLAlchemy Match model"""
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    score = Column(Float)
    is_applied = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    match_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship("UserDB")
    resume = relationship("ResumeDB")
    job = relationship("JobDB")


# Pydantic models for request/response
class MatchBase(BaseModel):
    user_id: int
    resume_id: int
    job_id: int
    score: float
    is_applied: bool = False
    is_favorite: bool = False
    match_data: Optional[Dict[str, Any]] = None


class MatchCreate(BaseModel):
    resume_id: int
    job_id: int
    score: Optional[float] = None
    match_data: Optional[Dict[str, Any]] = None


class MatchUpdate(BaseModel):
    score: Optional[float] = None
    is_applied: Optional[bool] = None
    is_favorite: Optional[bool] = None
    match_data: Optional[Dict[str, Any]] = None


class Match(MatchBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class MatchResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int
    score: float
    is_applied: bool
    is_favorite: bool
    match_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    job_title: str
    job_company: str
    job_location: str
    resume_title: str

    class Config:
        orm_mode = True


class MatchResult(BaseModel):
    """Match result for a resume and job"""
    resume_id: int
    job_id: int
    score: float
    match_factors: Dict[str, float]
    skills_matched: List[str]
    skills_missing: List[str]
    keywords_matched: List[str]
    recommendations: List[str] 