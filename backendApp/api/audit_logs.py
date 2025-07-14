# --- File: backendApp/api/audit_logs.py ---
# This file defines API endpoints for Audit Log resources.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backendApp.schemas.audit_log_schemas import AuditLogCreate, AuditLogResponse
from backendApp.services.audit_service import AuditService
from backendApp.dependencies import get_db # Import get_db from dependencies

import uuid
from typing import List

router = APIRouter()
audit_service = AuditService()

@router.post("/", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
def create_audit_log_api(audit_log: AuditLogCreate, db: Session = Depends(get_db)):
    db_audit_log = audit_service.create_audit_log(db, audit_log)
    if not db_audit_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for this audit log")
    return db_audit_log

@router.get("/{log_id}", response_model=AuditLogResponse)
def get_audit_log_api(log_id: uuid.UUID, db: Session = Depends(get_db)):
    audit_log = audit_service.get_audit_log(db, log_id)
    if not audit_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found")
    return audit_log

@router.get("/user/{user_id}", response_model=List[AuditLogResponse])
def get_user_audit_logs_api(user_id: uuid.UUID, db: Session = Depends(get_db)):
    audit_logs = audit_service.get_user_audit_logs(db, user_id)
    return audit_logs