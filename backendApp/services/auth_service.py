# backendApp/services/auth_service.py (NEW FILE)
import os
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, status
from typing import Optional # Import Optional

from backendApp.models.postgres_models import User, Quota
from backendApp.schemas.user_schemas import UserCreate
from backendApp.schemas.auth_schemas import LoginRequest, TokenData

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
# IMPORTANT: Change this to a strong, random string in production!
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-that-should-be-changed")
ALGORITHM = "HS256"

class AuthService:
    # Moved ACCESS_TOKEN_EXPIRE_MINUTES inside the class as a class attribute
    ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Token valid for 30 minutes

    def __init__(self):
        self.pwd_context = pwd_context
        # Ensure SECRET_KEY is set, otherwise raise an error
        if not SECRET_KEY or SECRET_KEY == "your-super-secret-key-that-should-be-changed":
            print("WARNING: SECRET_KEY is not set or is using the default value. Please set it in your .env file for production!")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def create_user(self, db: Session, user: UserCreate):
        # Check if user with this email already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            return None # Indicate that user already exists

        hashed_password = self.get_password_hash(user.password)
        db_user = User(
            name=user.name,
            email=user.email,
            password_hash=hashed_password,
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

    def authenticate_user(self, db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user or not self.verify_password(password, user.password_hash):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            # Use the class attribute ACCESS_TOKEN_EXPIRE_MINUTES
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def get_user_from_token(self, db: Session, token: str) -> User:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise JWTError("Invalid token payload")
            token_data = TokenData(email=email)
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e
        user = db.query(User).filter(User.email == token_data.email).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
