from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_, and_

from services.database import get_db
from services.user_service.utils.auth import get_current_active_user
from services.user_service.models.user import UserDB
from services.job_service.models.job import JobDB, Job, JobCreate, JobSource, JobSourceDB, JobSourceCreate
from agent.scraper import fetch_jobs

router = APIRouter()


@router.get("/", response_model=List[Job])
def read_jobs(
    skip: int = 0,
    limit: int = 100,
    title: Optional[str] = None,
    company: Optional[str] = None,
    location: Optional[str] = None,
    remote: Optional[bool] = None,
    job_type: Optional[str] = None,
    min_salary: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get all jobs with optional filters"""
    query = db.query(JobDB)
    
    # Apply filters
    if title:
        query = query.filter(JobDB.title.ilike(f"%{title}%"))
    if company:
        query = query.filter(JobDB.company.ilike(f"%{company}%"))
    if location:
        query = query.filter(JobDB.location.ilike(f"%{location}%"))
    if remote is not None:
        query = query.filter(JobDB.remote == remote)
    if job_type:
        query = query.filter(JobDB.job_type.ilike(f"%{job_type}%"))
    if min_salary:
        query = query.filter(or_(
            JobDB.salary_min >= min_salary,
            and_(JobDB.salary_min.is_(None), JobDB.salary_max >= min_salary)
        ))
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs


@router.get("/search", response_model=List[Job])
def search_jobs(
    q: str = Query(..., description="Search query"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Search jobs by keyword"""
    query = db.query(JobDB).filter(
        or_(
            JobDB.title.ilike(f"%{q}%"),
            JobDB.company.ilike(f"%{q}%"),
            JobDB.location.ilike(f"%{q}%"),
            JobDB.description.ilike(f"%{q}%")
        )
    )
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=Job)
def read_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Get job by ID"""
    job = db.query(JobDB).filter(JobDB.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/sources", response_model=JobSource, status_code=status.HTTP_201_CREATED)
def create_job_source(
    source: JobSourceCreate,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new job source"""
    # Check if source with name exists
    db_source = db.query(JobSourceDB).filter(JobSourceDB.name == source.name).first()
    if db_source:
        raise HTTPException(status_code=400, detail="Source with this name already exists")
    
    # Create source
    db_source = JobSourceDB(
        name=source.name,
        url=source.url,
        is_active=source.is_active
    )
    
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    
    return db_source


@router.get("/sources", response_model=List[JobSource])
def read_job_sources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all job sources"""
    sources = db.query(JobSourceDB).offset(skip).limit(limit).all()
    return sources


@router.post("/scrape", response_model=List[Job])
def scrape_jobs(
    keywords: List[str] = Query(None),
    locations: List[str] = Query(None),
    limit: int = Query(100),
    current_user: UserDB = Depends(get_current_active_user),
):
    """Scrape jobs from configured sources"""
    # Check if user is premium
    if not current_user.is_premium:
        raise HTTPException(status_code=403, detail="This feature is only available for premium users")
    
    # Scrape jobs
    jobs = fetch_jobs(keywords, locations, limit)
    return jobs 