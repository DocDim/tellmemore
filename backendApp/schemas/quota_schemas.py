# --- File: backendApp/schemas/quota_schemas.py ---
# This file defines Pydantic schemas for Quota related data.

from pydantic import BaseModel, ConfigDict
from typing import Optional
import uuid
from datetime import datetime

class QuotaBase(BaseModel):
    daily_limit: int = 100
    used_today: int = 0
    last_reset: Optional[datetime] = None

class QuotaResponse(QuotaBase):
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)