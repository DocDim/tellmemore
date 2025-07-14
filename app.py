# TELLMEMORE_BACKEND/app.py (Backend API Only)
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from backendApp.models.postgres_models import Base
from backendApp.dependencies import engine
from backendApp.api.users import router as users_router
from backendApp.api.chat_sessions import router as chat_sessions_router
from backendApp.api.prompts import router as prompts_router
from backendApp.api.audit_logs import router as audit_logs_router
from backendApp.api.auth import router as auth_router # Import the auth router

# --- Lifespan Context Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    Creates database tables on startup.
    """
    port = os.getenv("PORT", "8000")
    print(f"Backend Application startup on port {port} (from environment variable/default)...")
    Base.metadata.create_all(bind=engine) # Create database tables
    print("Database tables created/checked.")
    yield
    print("Backend Application shutdown.")

# --- FastAPI Application ---
app = FastAPI(
    title="LLM Interaction API",
    description="API for managing users, chat sessions, prompts, quotas, and audit logs for an LLM application.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs", # API documentation URL
    redoc_url="/api/v1/redoc" # Redoc documentation URL
)

# --- CORS Configuration ---
# Get allowed origins from environment variable, split by comma
# This should include the URL of your separate frontend application (e.g., http://localhost:8080)
origins = os.getenv("CORS_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Allows specific origins
    allow_credentials=True, # Allow cookies to be included in cross-origin HTTP requests
    allow_methods=["*"],    # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allow all headers
)

# --- Main API Router for /api/v1 prefix ---
api_v1_router = APIRouter(prefix="/api/v1")

# --- Include API Routers within the api_v1_router ---
# All API endpoints will be prefixed with /api/v1
api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"]) # Auth endpoints like /api/v1/auth/login
api_v1_router.include_router(users_router, prefix="/users", tags=["Users"])
api_v1_router.include_router(chat_sessions_router, prefix="/chat_sessions", tags=["Chat Sessions"])
api_v1_router.include_router(prompts_router, prefix="/prompts", tags=["Prompts"])
api_v1_router.include_router(audit_logs_router, prefix="/audit_logs", tags=["Audit Logs"])

# Include the main api_v1_router in the FastAPI app
app.include_router(api_v1_router)
print("api_v1_router has been included in the main app.")

# Root endpoint for basic backend API check (not serving frontend HTML)
@app.get("/")
def read_root():
    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "8000")
    base_api_url = f"http://{host}:{port}/api/v1"
    return {"message": f"Welcome to the LLM Interaction API! Access documentation at {base_api_url}/docs"}
