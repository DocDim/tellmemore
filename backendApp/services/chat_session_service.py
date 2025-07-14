# --- File: backendApp/services/chat_session_service.py ---
# This file contains the business logic for Chat Session operations.

from sqlalchemy.orm import Session
from backendApp.models.postgres_models import ChatSession, User
from backendApp.schemas.chat_session_schemas import ChatSessionCreate, ChatSessionBase
import uuid

class ChatSessionService:
    def create_chat_session(self, db: Session, session: ChatSessionCreate):
        # Ensure user exists before creating session
        user = db.query(User).filter(User.user_id == session.user_id).first()
        if not user:
            return None # Or raise a specific error to be handled by API layer
        db_session = ChatSession(**session.dict())
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    def get_chat_session(self, db: Session, session_id: uuid.UUID):
        return db.query(ChatSession).filter(ChatSession.session_id == session_id).first()

    def get_user_chat_sessions(self, db: Session, user_id: uuid.UUID):
        return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

    def update_chat_session(self, db: Session, session_id: uuid.UUID, session_update: ChatSessionBase):
        session = self.get_chat_session(db, session_id)
        if session:
            for key, value in session_update.dict(exclude_unset=True).items():
                setattr(session, key, value)
            db.commit()
            db.refresh(session)
        return session

    def delete_chat_session(self, db: Session, session_id: uuid.UUID):
        session = self.get_chat_session(db, session_id)
        if session:
            db.delete(session)
            db.commit()
            return True
        return False