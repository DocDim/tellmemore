# --- File: backendApp/services/user_service.py ---
# This file contains the business logic for User operations.

from sqlalchemy.orm import Session
from backendApp.models.postgres_models import User, Quota
from backendApp.schemas.user_schemas import UserCreate, UserBase
from backendApp.schemas.quota_schemas import QuotaBase
import uuid

class UserService:
    def create_user(self, db: Session, user: UserCreate):
        db_user = User(
            name=user.name,
            email=user.email,
            password_hash=user.password, # In real app, hash this password
            role=user.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        # Create a default quota for the new user
        db_quota = Quota(user_id=db_user.user_id)
        db.add(db_quota)
        db.commit()
        db.refresh(db_quota)
        return db_user

    def get_user(self, db: Session, user_id: uuid.UUID):
        return db.query(User).filter(User.user_id == user_id).first()

    def update_user(self, db: Session, user_id: uuid.UUID, user_update: UserBase):
        user = self.get_user(db, user_id)
        if user:
            for key, value in user_update.dict(exclude_unset=True).items():
                setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user

    def delete_user(self, db: Session, user_id: uuid.UUID):
        user = self.get_user(db, user_id)
        if user:
            db.delete(user)
            db.commit()
            return True
        return False