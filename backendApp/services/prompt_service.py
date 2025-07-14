# --- File: backendApp/services/prompt_service.py ---
# This file contains the business logic for Prompt operations.

from sqlalchemy.orm import Session
from backendApp.models.postgres_models import Prompt, User, ChatSession
from backendApp.schemas.prompt_schemas import PromptCreate, PromptBase
import uuid

class PromptService:
    def create_prompt(self, db: Session, prompt: PromptCreate):
        # Ensure user and session exist
        user = db.query(User).filter(User.user_id == prompt.user_id).first()
        session = db.query(ChatSession).filter(ChatSession.session_id == prompt.session_id).first()
        if not user or not session:
            return None # Or raise a specific error
        db_prompt = Prompt(**prompt.dict())
        db.add(db_prompt)
        db.commit()
        db.refresh(db_prompt)
        return db_prompt

    def get_prompt(self, db: Session, prompt_id: uuid.UUID):
        return db.query(Prompt).filter(Prompt.prompt_id == prompt_id).first()

    def get_session_prompts(self, db: Session, session_id: uuid.UUID):
        return db.query(Prompt).filter(Prompt.session_id == session_id).all()

    def update_prompt(self, db: Session, prompt_id: uuid.UUID, prompt_update: PromptBase):
        prompt = self.get_prompt(db, prompt_id)
        if prompt:
            for key, value in prompt_update.dict(exclude_unset=True).items():
                setattr(prompt, key, value)
            db.commit()
            db.refresh(prompt)
        return prompt

    def delete_prompt(self, db: Session, prompt_id: uuid.UUID):
        prompt = self.get_prompt(db, prompt_id)
        if prompt:
            db.delete(prompt)
            db.commit()
            return True
        return False