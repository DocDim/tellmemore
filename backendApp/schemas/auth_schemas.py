# backendApp/schemas/auth_schemas.py 
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class LoginRequest(BaseModel):
    username: EmailStr # Using username for email in OAuth2PasswordRequestForm
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
