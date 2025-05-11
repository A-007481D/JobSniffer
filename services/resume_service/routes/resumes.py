import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List

from services.database import get_db
from services.user_service.utils.auth import get_current_active_user
from services.user_service.models.user import UserDB
from services.resume_service.models.resume import ResumeDB, Resume, ResumeCreate, ResumeUpdate, SkillDB, Skill, SkillCreate

router = APIRouter()


@router.post("/", response_model=Resume, status_code=status.HTTP_201_CREATED)
def create_resume(
    resume: ResumeCreate,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new resume"""
    # Create resume
    db_resume = ResumeDB(
        user_id=current_user.id,
        title=resume.title,
        content=resume.content,
        parsed_data=resume.parsed_data,
        file_path=resume.file_path
    )
    
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    
    return db_resume


@router.post("/upload", response_model=Resume, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    title: str = Form(...),
    resume_file: UploadFile = File(...),
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a resume file"""
    # Create directory if it doesn't exist
    upload_dir = os.path.join("uploads", "resumes", str(current_user.id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_dir, resume_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume_file.file, buffer)
    
    # Create resume
    db_resume = ResumeDB(
        user_id=current_user.id,
        title=title,
        file_path=file_path
    )
    
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    
    return db_resume


@router.get("/", response_model=List[Resume])
def read_resumes(
    skip: int = 0,
    limit: int = 100,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all resumes for current user"""
    resumes = db.query(ResumeDB).filter(ResumeDB.user_id == current_user.id).offset(skip).limit(limit).all()
    return resumes


@router.get("/{resume_id}", response_model=Resume)
def read_resume(
    resume_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get resume by ID"""
    resume = db.query(ResumeDB).filter(ResumeDB.id == resume_id, ResumeDB.user_id == current_user.id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.put("/{resume_id}", response_model=Resume)
def update_resume(
    resume_id: int,
    resume_update: ResumeUpdate,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update resume by ID"""
    db_resume = db.query(ResumeDB).filter(ResumeDB.id == resume_id, ResumeDB.user_id == current_user.id).first()
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Update resume fields
    for key, value in resume_update.dict(exclude_unset=True).items():
        setattr(db_resume, key, value)
    
    db.commit()
    db.refresh(db_resume)
    
    return db_resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete resume by ID"""
    db_resume = db.query(ResumeDB).filter(ResumeDB.id == resume_id, ResumeDB.user_id == current_user.id).first()
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete resume
    db.delete(db_resume)
    db.commit()
    
    return None


# Skills routes
@router.post("/{resume_id}/skills", response_model=Skill, status_code=status.HTTP_201_CREATED)
def create_skill(
    resume_id: int,
    skill: SkillCreate,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new skill for a resume"""
    # Check if resume exists and belongs to user
    db_resume = db.query(ResumeDB).filter(ResumeDB.id == resume_id, ResumeDB.user_id == current_user.id).first()
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Create skill
    db_skill = SkillDB(
        resume_id=resume_id,
        name=skill.name,
        category=skill.category,
        level=skill.level
    )
    
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    
    return db_skill


@router.get("/{resume_id}/skills", response_model=List[Skill])
def read_skills(
    resume_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all skills for a resume"""
    # Check if resume exists and belongs to user
    db_resume = db.query(ResumeDB).filter(ResumeDB.id == resume_id, ResumeDB.user_id == current_user.id).first()
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Get skills
    skills = db.query(SkillDB).filter(SkillDB.resume_id == resume_id).all()
    return skills 