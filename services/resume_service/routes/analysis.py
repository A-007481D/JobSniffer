from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from services.database import get_db
from services.user_service.utils.auth import get_current_active_user
from services.user_service.models.user import UserDB
from services.resume_service.models.resume import ResumeDB, ResumeAnalysis
from agent.ai_module import ResumeAI

router = APIRouter()
resume_ai = ResumeAI()


@router.post("/{resume_id}/analyze", response_model=ResumeAnalysis)
def analyze_resume(
    resume_id: int,
    job_description: Dict[str, Any] = None,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze resume and provide suggestions"""
    # Check if resume exists and belongs to user
    db_resume = db.query(ResumeDB).filter(ResumeDB.id == resume_id, ResumeDB.user_id == current_user.id).first()
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Get resume content
    resume_content = db_resume.content
    if not resume_content:
        raise HTTPException(status_code=400, detail="Resume content is empty")
    
    # Analyze resume
    job_desc_text = job_description.get("description", "") if job_description else None
    analysis = resume_ai.analyze_resume(resume_content, job_desc_text)
    
    # Return analysis
    return {
        "resume_id": resume_id,
        "suggestions": analysis.get("suggestions", []),
        "keywords": analysis.get("keywords", []),
        "score": analysis.get("score", 0.0),
        "improvement_areas": analysis.get("improvement_areas", [])
    }


@router.post("/{resume_id}/enhance", response_model=Dict[str, Any])
def enhance_resume(
    resume_id: int,
    job_description: Dict[str, Any] = None,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enhance resume based on job description"""
    # Check if resume exists and belongs to user
    db_resume = db.query(ResumeDB).filter(ResumeDB.id == resume_id, ResumeDB.user_id == current_user.id).first()
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Get resume content
    resume_content = db_resume.content
    if not resume_content:
        raise HTTPException(status_code=400, detail="Resume content is empty")
    
    # Enhance resume
    job_desc_text = job_description.get("description", "") if job_description else None
    enhanced_content = resume_ai.enhance_resume(resume_content, job_desc_text)
    
    # Update resume content
    db_resume.content = enhanced_content
    db.commit()
    
    return {
        "resume_id": resume_id,
        "enhanced_content": enhanced_content
    } 