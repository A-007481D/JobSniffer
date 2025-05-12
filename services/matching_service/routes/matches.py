from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any

from services.database import get_db
from services.user_service.utils.auth import get_current_active_user
from services.user_service.models.user import UserDB
from services.resume_service.models.resume import ResumeDB
from services.job_service.models.job import JobDB
from services.matching_service.models.match import MatchDB, Match, MatchCreate, MatchUpdate, MatchResponse, MatchResult
from agent.matcher import JobMatcher

router = APIRouter()
job_matcher = JobMatcher()


@router.post("/", response_model=Match, status_code=status.HTTP_201_CREATED)
def create_match(
    match: MatchCreate,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new match"""
    # Check if resume exists and belongs to user
    resume = db.query(ResumeDB).filter(ResumeDB.id == match.resume_id, ResumeDB.user_id == current_user.id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Check if job exists
    job = db.query(JobDB).filter(JobDB.id == match.job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if match already exists
    existing_match = db.query(MatchDB).filter(
        MatchDB.user_id == current_user.id,
        MatchDB.resume_id == match.resume_id,
        MatchDB.job_id == match.job_id
    ).first()
    
    if existing_match:
        raise HTTPException(status_code=400, detail="Match already exists")
    
    # Create match
    score = match.score
    match_data = match.match_data
    
    # If score is not provided, calculate it
    if score is None or match_data is None:
        if resume.content and job.description:
            match_result = job_matcher.match_resume_with_job(resume.content, job.description)
            score = match_result["score"]
            match_data = match_result
    
    db_match = MatchDB(
        user_id=current_user.id,
        resume_id=match.resume_id,
        job_id=match.job_id,
        score=score,
        match_data=match_data
    )
    
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    
    return db_match


@router.get("/", response_model=List[MatchResponse])
def read_matches(
    skip: int = 0,
    limit: int = 100,
    resume_id: Optional[int] = None,
    job_id: Optional[int] = None,
    min_score: Optional[float] = None,
    is_applied: Optional[bool] = None,
    is_favorite: Optional[bool] = None,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all matches for current user with optional filters"""
    query = db.query(
        MatchDB,
        JobDB.title.label("job_title"),
        JobDB.company.label("job_company"),
        JobDB.location.label("job_location"),
        ResumeDB.title.label("resume_title")
    ).join(
        JobDB, MatchDB.job_id == JobDB.id
    ).join(
        ResumeDB, MatchDB.resume_id == ResumeDB.id
    ).filter(
        MatchDB.user_id == current_user.id
    )
    
    # Apply filters
    if resume_id:
        query = query.filter(MatchDB.resume_id == resume_id)
    if job_id:
        query = query.filter(MatchDB.job_id == job_id)
    if min_score:
        query = query.filter(MatchDB.score >= min_score)
    if is_applied is not None:
        query = query.filter(MatchDB.is_applied == is_applied)
    if is_favorite is not None:
        query = query.filter(MatchDB.is_favorite == is_favorite)
    
    # Order by score descending
    query = query.order_by(desc(MatchDB.score))
    
    # Get matches
    results = query.offset(skip).limit(limit).all()
    
    # Convert to response model
    matches = []
    for result in results:
        match_db, job_title, job_company, job_location, resume_title = result
        matches.append({
            "id": match_db.id,
            "user_id": match_db.user_id,
            "resume_id": match_db.resume_id,
            "job_id": match_db.job_id,
            "score": match_db.score,
            "is_applied": match_db.is_applied,
            "is_favorite": match_db.is_favorite,
            "match_data": match_db.match_data,
            "created_at": match_db.created_at,
            "updated_at": match_db.updated_at,
            "job_title": job_title,
            "job_company": job_company,
            "job_location": job_location,
            "resume_title": resume_title
        })
    
    return matches


@router.get("/{match_id}", response_model=MatchResponse)
def read_match(
    match_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get match by ID"""
    result = db.query(
        MatchDB,
        JobDB.title.label("job_title"),
        JobDB.company.label("job_company"),
        JobDB.location.label("job_location"),
        ResumeDB.title.label("resume_title")
    ).join(
        JobDB, MatchDB.job_id == JobDB.id
    ).join(
        ResumeDB, MatchDB.resume_id == ResumeDB.id
    ).filter(
        MatchDB.id == match_id,
        MatchDB.user_id == current_user.id
    ).first()
    
    if result is None:
        raise HTTPException(status_code=404, detail="Match not found")
    
    match_db, job_title, job_company, job_location, resume_title = result
    
    return {
        "id": match_db.id,
        "user_id": match_db.user_id,
        "resume_id": match_db.resume_id,
        "job_id": match_db.job_id,
        "score": match_db.score,
        "is_applied": match_db.is_applied,
        "is_favorite": match_db.is_favorite,
        "match_data": match_db.match_data,
        "created_at": match_db.created_at,
        "updated_at": match_db.updated_at,
        "job_title": job_title,
        "job_company": job_company,
        "job_location": job_location,
        "resume_title": resume_title
    }


@router.put("/{match_id}", response_model=Match)
def update_match(
    match_id: int,
    match_update: MatchUpdate,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update match by ID"""
    db_match = db.query(MatchDB).filter(MatchDB.id == match_id, MatchDB.user_id == current_user.id).first()
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Update match fields
    for key, value in match_update.dict(exclude_unset=True).items():
        setattr(db_match, key, value)
    
    db.commit()
    db.refresh(db_match)
    
    return db_match


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(
    match_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete match by ID"""
    db_match = db.query(MatchDB).filter(MatchDB.id == match_id, MatchDB.user_id == current_user.id).first()
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Delete match
    db.delete(db_match)
    db.commit()
    
    return None


@router.post("/analyze", response_model=MatchResult)
def analyze_match(
    resume_id: int,
    job_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze match between resume and job"""
    # Check if resume exists and belongs to user
    resume = db.query(ResumeDB).filter(ResumeDB.id == resume_id, ResumeDB.user_id == current_user.id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Check if job exists
    job = db.query(JobDB).filter(JobDB.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if resume has content
    if not resume.content:
        raise HTTPException(status_code=400, detail="Resume has no content")
    
    # Check if job has description
    if not job.description:
        raise HTTPException(status_code=400, detail="Job has no description")
    
    # Analyze match
    match_result = job_matcher.match_resume_with_job(resume.content, job.description)
    
    return {
        "resume_id": resume_id,
        "job_id": job_id,
        "score": match_result["score"],
        "match_factors": match_result["match_factors"],
        "skills_matched": match_result["skills_matched"],
        "skills_missing": match_result["skills_missing"],
        "keywords_matched": match_result["keywords_matched"],
        "recommendations": match_result["recommendations"]
    }


@router.post("/batch", response_model=List[Dict[str, Any]])
def batch_match_jobs(
    resume_id: int,
    limit: int = Query(10, ge=1, le=100),
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Match resume with multiple jobs and return ranked matches"""
    # Check if resume exists and belongs to user
    resume = db.query(ResumeDB).filter(ResumeDB.id == resume_id, ResumeDB.user_id == current_user.id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Check if resume has content
    if not resume.content:
        raise HTTPException(status_code=400, detail="Resume has no content")
    
    # Get jobs
    jobs = db.query(JobDB).limit(100).all()
    
    if not jobs:
        return []
    
    # Convert jobs to dict
    job_dicts = []
    for job in jobs:
        job_dicts.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description
        })
    
    # Match resume with jobs
    matches = job_matcher.batch_match_jobs(resume.content, job_dicts)
    
    # Limit results
    return matches[:limit] 