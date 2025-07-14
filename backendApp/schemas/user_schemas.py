# --- File: backendApp/schemas/user_schemas.py ---
# This file defines Pydantic schemas for User related data.

from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
import uuid
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Optional[str] = "user"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)