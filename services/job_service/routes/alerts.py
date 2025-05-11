from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from services.database import get_db
from services.user_service.utils.auth import get_current_active_user
from services.user_service.models.user import UserDB
from services.job_service.models.job import JobAlertDB, JobAlert, JobAlertCreate, JobAlertUpdate

router = APIRouter()


@router.post("/", response_model=JobAlert, status_code=status.HTTP_201_CREATED)
def create_job_alert(
    alert: JobAlertCreate,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new job alert"""
    db_alert = JobAlertDB(
        user_id=current_user.id,
        title=alert.title,
        keywords=alert.keywords,
        locations=alert.locations,
        job_types=alert.job_types,
        remote=alert.remote,
        salary_min=alert.salary_min,
        is_active=alert.is_active
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return db_alert


@router.get("/", response_model=List[JobAlert])
def read_job_alerts(
    skip: int = 0,
    limit: int = 100,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all job alerts for current user"""
    alerts = db.query(JobAlertDB).filter(JobAlertDB.user_id == current_user.id).offset(skip).limit(limit).all()
    return alerts


@router.get("/{alert_id}", response_model=JobAlert)
def read_job_alert(
    alert_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get job alert by ID"""
    alert = db.query(JobAlertDB).filter(JobAlertDB.id == alert_id, JobAlertDB.user_id == current_user.id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Job alert not found")
    return alert


@router.put("/{alert_id}", response_model=JobAlert)
def update_job_alert(
    alert_id: int,
    alert_update: JobAlertUpdate,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update job alert by ID"""
    db_alert = db.query(JobAlertDB).filter(JobAlertDB.id == alert_id, JobAlertDB.user_id == current_user.id).first()
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Job alert not found")
    
    # Update alert fields
    for key, value in alert_update.dict(exclude_unset=True).items():
        setattr(db_alert, key, value)
    
    db.commit()
    db.refresh(db_alert)
    
    return db_alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_alert(
    alert_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete job alert by ID"""
    db_alert = db.query(JobAlertDB).filter(JobAlertDB.id == alert_id, JobAlertDB.user_id == current_user.id).first()
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Job alert not found")
    
    # Delete alert
    db.delete(db_alert)
    db.commit()
    
    return None 