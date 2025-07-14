# --- File: backendApp/services/quota_service.py ---
# This file contains the business logic for Quota operations.

from sqlalchemy.orm import Session
from backendApp.models.postgres_models import Quota
from backendApp.schemas.quota_schemas import QuotaBase
import uuid

class QuotaService:
    def get_user_quota(self, db: Session, user_id: uuid.UUID):
        return db.query(Quota).filter(Quota.user_id == user_id).first()

    def update_user_quota(self, db: Session, user_id: uuid.UUID, quota_update: QuotaBase):
        quota = self.get_user_quota(db, user_id)
        if quota:
            for key, value in quota_update.dict(exclude_unset=True).items():
                setattr(quota, key, value)
            db.commit()
            db.refresh(quota)
        return quota