from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from services.database import Base
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class UserActivityDB(Base):
    """SQLAlchemy UserActivity model"""
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String)  # login, search, view_job, apply_job, etc.
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("UserDB")


class JobMarketTrendDB(Base):
    """SQLAlchemy JobMarketTrend model"""
    __tablename__ = "job_market_trends"

    id = Column(Integer, primary_key=True, index=True)
    skill = Column(String, index=True)
    demand_score = Column(Float)
    growth_rate = Column(Float)
    avg_salary = Column(Float)
    data_points = Column(Integer)
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserInsightDB(Base):
    """SQLAlchemy UserInsight model"""
    __tablename__ = "user_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    insight_type = Column(String)  # skill_gap, job_match_trend, application_success, etc.
    title = Column(String)
    description = Column(String)
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("UserDB")

# Pydantic models for request/response
class UserActivity(BaseModel):
    id: int
    user_id: int
    activity_type: str
    details: Dict[str, Any]
    created_at: datetime

    class Config:
        orm_mode = True


class UserActivityCreate(BaseModel):
    user_id: int
    activity_type: str
    details: Dict[str, Any]


class JobMarketTrend(BaseModel):
    id: int
    skill: str
    demand_score: float
    growth_rate: float
    avg_salary: float
    data_points: int
    details: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        orm_mode = True


class UserInsight(BaseModel):
    id: int
    user_id: int
    insight_type: str
    title: str
    description: str
    data: Dict[str, Any]
    created_at: datetime

    class Config:
        orm_mode = True


class UserInsightCreate(BaseModel):
    user_id: int
    insight_type: str
    title: str
    description: str
    data: Dict[str, Any]


class SkillGapAnalysis(BaseModel):
    user_id: int
    missing_skills: List[str]
    skill_market_data: List[Dict[str, Any]]
    recommendations: List[str]


class JobMarketAnalysis(BaseModel):
    top_skills: List[Dict[str, Any]]
    trending_skills: List[Dict[str, Any]]
    salary_ranges: Dict[str, Dict[str, float]]
    job_growth_areas: List[Dict[str, Any]] 