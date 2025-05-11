from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from services.database import get_db
from services.user_service.models.user import UserDB, User, UserCreate, UserUpdate
from services.user_service.utils.auth import get_password_hash, get_current_active_user

router = APIRouter()


@router.post(
    "/", 
    response_model=User, 
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create a new user in the system",
    responses={
        400: {"description": "Email already registered or username already taken"},
        201: {"description": "User created successfully"}
    }
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with the following information:
    
    - **email**: Required unique email
    - **username**: Required unique username
    - **password**: Required password (min length 8)
    - **first_name**: Optional first name
    - **last_name**: Optional last name
    """
    # Check if user with email exists
    db_user_email = db.query(UserDB).filter(UserDB.email == user.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if user with username exists
    db_user_username = db.query(UserDB).filter(UserDB.username == user.username).first()
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    hashed_password = get_password_hash(user.password)
    db_user = UserDB(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get(
    "/me", 
    response_model=User,
    summary="Get current user",
    description="Get profile information for the currently authenticated user",
    responses={
        401: {"description": "Not authenticated or inactive user"}
    }
)
def read_users_me(current_user: UserDB = Depends(get_current_active_user)):
    """
    Get current user profile information.
    
    This endpoint requires authentication.
    """
    return current_user


@router.put(
    "/me", 
    response_model=User,
    summary="Update current user",
    description="Update profile information for the currently authenticated user",
    responses={
        401: {"description": "Not authenticated or inactive user"}
    }
)
def update_user_me(
    user_update: UserUpdate,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile with the following optional information:
    
    - **email**: New email address
    - **username**: New username
    - **first_name**: First name
    - **last_name**: Last name
    - **profile_picture**: URL to profile picture
    - **bio**: Short biography (max length 500)
    - **is_active**: Whether the user is active
    - **is_premium**: Whether the user has premium status
    
    This endpoint requires authentication.
    """
    # Check if email is being updated and is not already taken
    if user_update.email and user_update.email != current_user.email:
        db_user = db.query(UserDB).filter(UserDB.email == user_update.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username is being updated and is not already taken
    if user_update.username and user_update.username != current_user.username:
        db_user = db.query(UserDB).filter(UserDB.username == user_update.username).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Update user fields
    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get(
    "/{user_id}", 
    response_model=User,
    summary="Get user by ID",
    description="Get user information by user ID",
    responses={
        404: {"description": "User not found"}
    }
)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user by ID.
    
    - **user_id**: Required user ID
    """
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get(
    "/", 
    response_model=List[User],
    summary="Get users",
    description="Get a list of users with optional filtering"
)
def read_users(
    skip: int = Query(0, description="Number of users to skip"),
    limit: int = Query(100, description="Maximum number of users to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_premium: Optional[bool] = Query(None, description="Filter by premium status"),
    db: Session = Depends(get_db)
):
    """
    Get a list of users with optional filtering.
    
    - **skip**: Number of users to skip
    - **limit**: Maximum number of users to return
    - **is_active**: Filter by active status
    - **is_premium**: Filter by premium status
    """
    query = db.query(UserDB)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(UserDB.is_active == is_active)
    
    if is_premium is not None:
        query = query.filter(UserDB.is_premium == is_premium)
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    return users 