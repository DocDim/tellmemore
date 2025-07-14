# --- File: backendApp/api/users.py ---
# This file defines API endpoints for User and Quota resources.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backendApp.schemas.user_schemas import UserCreate, UserBase, UserResponse
from backendApp.schemas.quota_schemas import QuotaBase, QuotaResponse
from backendApp.services.user_service import UserService
from backendApp.services.quota_service import QuotaService
from backendApp.dependencies import get_db # Import get_db from dependencies

import uuid

router = APIRouter()
user_service = UserService()
quota_service = QuotaService()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_api(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.create_user(db, user)
    return db_user

@router.get("/{user_id}", response_model=UserResponse)
def get_user_api(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user_api(user_id: uuid.UUID, user_update: UserBase, db: Session = Depends(get_db)):
    user = user_service.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_api(user_id: uuid.UUID, db: Session = Depends(get_db)):
    if not user_service.delete_user(db, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User deleted successfully"}

@router.get("/{user_id}/quota", response_model=QuotaResponse)
def get_user_quota_api(user_id: uuid.UUID, db: Session = Depends(get_db)):
    quota = quota_service.get_user_quota(db, user_id)
    if not quota:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quota not found for this user")
    return quota

@router.put("/{user_id}/quota", response_model=QuotaResponse)
def update_user_quota_api(user_id: uuid.UUID, quota_update: QuotaBase, db: Session = Depends(get_db)):
    quota = quota_service.update_user_quota(db, user_id, quota_update)
    if not quota:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quota not found for this user")
    return quota