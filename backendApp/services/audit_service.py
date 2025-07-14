# --- File: backendApp/services/audit_service.py ---
# This file contains the business logic for Audit Log operations.

from sqlalchemy.orm import Session
from backendApp.models.postgres_models import AuditLog, User
from backendApp.schemas.audit_log_schemas import AuditLogCreate
import uuid

class AuditService:
    def create_audit_log(self, db: Session, audit_log: AuditLogCreate):
        # Ensure user exists
        user = db.query(User).filter(User.user_id == audit_log.user_id).first()
        if not user:
            return None # Or raise a specific error
        db_audit_log = AuditLog(**audit_log.dict())
        db.add(db_audit_log)
        db.commit()
        db.refresh(db_audit_log)
        return db_audit_log

    def get_audit_log(self, db: Session, log_id: uuid.UUID):
        return db.query(AuditLog).filter(AuditLog.log_id == log_id).first()

    def get_user_audit_logs(self, db: Session, user_id: uuid.UUID):
        return db.query(AuditLog).filter(AuditLog.user_id == user_id).all()