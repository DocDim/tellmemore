# --- File: backendApp/schemas/chat_session_schemas.py ---
# This file defines Pydantic schemas for Chat Session related data.

from pydantic import BaseModel, ConfigDict
from typing import Optional
import uuid
from datetime import datetime

class ChatSessionBase(BaseModel):
    title: str

class ChatSessionCreate(ChatSessionBase):
    user_id: uuid.UUID

class ChatSessionResponse(ChatSessionBase):
    session_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)