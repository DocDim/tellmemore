# --- File: backendApp/services/__init__.py ---
# This file makes the 'services' directory a Python package.
# It can also be used to export service instances.

from .user_service import UserService
from .quota_service import QuotaService
from .chat_session_service import ChatSessionService
from .prompt_service import PromptService
from .audit_service import AuditService
from .auth_service import AuthService # New import

user_service = UserService()
quota_service = QuotaService()
chat_session_service = ChatSessionService()
prompt_service = PromptService()
audit_service = AuditService()
auth_service = AuthService() # New service instance