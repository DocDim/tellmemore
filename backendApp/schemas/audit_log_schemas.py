# --- File: backendApp/schemas/audit_log_schemas.py ---
# This file defines Pydantic schemas for Audit Log related data.

from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

class AuditLogBase(BaseModel):
    action: str
    details: Optional[Dict[str, Any]] = None

class AuditLogCreate(AuditLogBase):
    user_id: uuid.UUID

class AuditLogResponse(AuditLogBase):
    log_id: uuid.UUID
    user_id: uuid.UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)