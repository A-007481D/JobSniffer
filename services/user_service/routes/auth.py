from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from services.database import get_db
from services.user_service.models.user import UserDB, Token, User
from services.user_service.utils.auth import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user
)

router = APIRouter()


@router.post(
    "/token", 
    response_model=Token,
    summary="Create access token",
    description="Get an access token for accessing protected endpoints",
    responses={
        401: {"description": "Invalid username or password"}
    }
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with username and password to get an access token.
    
    - **username**: The user's username
    - **password**: The user's password
    """
    # Check if user exists
    user = db.query(UserDB).filter(UserDB.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me/token-check", 
    response_model=User,
    summary="Verify token",
    description="Verify if the token is valid and return the current user's data",
    responses={
        401: {"description": "Invalid token or inactive user"}
    }
)
async def verify_token(current_user: UserDB = Depends(get_current_active_user)):
    """
    Verify if the token is valid and return the current user's data.
    
    This endpoint requires a valid authentication token in the request header.
    """
    return current_user 