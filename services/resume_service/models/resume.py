from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from services.database import Base
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ResumeDB(Base):
    """SQLAlchemy Resume model"""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    content = Column(Text)
    parsed_data = Column(JSON)
    file_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship("UserDB")


class SkillDB(Base):
    """SQLAlchemy Skill model"""
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    name = Column(String)
    category = Column(String)
    level = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resume = relationship("ResumeDB")


# Pydantic models for request/response
class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    level: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class Skill(SkillBase):
    id: int
    resume_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class ResumeBase(BaseModel):
    title: str
    content: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None


class Resume(ResumeBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    skills: List[Skill] = []

    class Config:
        orm_mode = True


class ResumeAnalysis(BaseModel):
    resume_id: int
    suggestions: List[str]
    keywords: List[str]
    score: float
    improvement_areas: List[str] 