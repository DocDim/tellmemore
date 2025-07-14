# --- File: backendApp/schemas/prompt_schemas.py ---
# This file defines Pydantic schemas for Prompt related data.

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime

class PromptBase(BaseModel):
    prompt_text: str
    llm_responses: Optional[List[str]] = []

class PromptCreate(PromptBase):
    user_id: uuid.UUID
    session_id: uuid.UUID

class PromptResponse(PromptBase):
    prompt_id: uuid.UUID
    user_id: uuid.UUID
    session_id: uuid.UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)