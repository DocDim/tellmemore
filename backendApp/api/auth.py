from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from backendApp.schemas.user_schemas import UserCreate, UserResponse
from backendApp.schemas.auth_schemas import Token, LoginRequest, TokenData
from backendApp.services.auth_service import AuthService
from backendApp.dependencies import get_db
from backendApp.models.postgres_models import User

router = APIRouter()
auth_service = AuthService()

# OAuth2PasswordBearer for token extraction from headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency to get the current authenticated user from a JWT token.
    Raises HTTPException if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = auth_service.get_user_from_token(db, token)
        if user is None:
            raise credentials_exception
        return user
    except Exception as e:
        # Catch any other exceptions during token decoding/user retrieval
        raise credentials_exception from e


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user in the system.
    """
    db_user = auth_service.create_user(db, user_create)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return db_user

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user and returns an access token.
    Uses OAuth2PasswordRequestForm for standard username/password login.
    """
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Define token expiration time (e.g., 30 minutes)
    access_token_expires = timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/protected", response_model=UserResponse)
def read_protected_data(current_user: User = Depends(get_current_user)):
    """
    An example protected endpoint that requires a valid JWT token.
    Returns the current authenticated user's details.
    """
    return current_user
