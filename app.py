# TELLMEMORE_FRONTEND_FASTAPI/app.py (Frontend Only)
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Import settings from your frontend's config.py
from config import settings
# Import the frontend router from your frontend's routes.py
from routes import router as frontend_router

# --- Lifespan Context Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the frontend application.
    """
    port = os.getenv("FRONTEND_PORT", "8080")
    print(f"Frontend Application startup on port {port} (from environment variable/default)...")
    # Diagnostic print to confirm the backend API URL loaded from frontend config
    print(f"DEBUG (frontend app.py): BACKEND_API_URL from config: {settings.BACKEND_API_URL}")
    print(f"DEBUG (frontend app.py): LLM_API_BASE_URL from config: {settings.LLM_API_BASE_URL}")
    yield
    print("Frontend Application shutdown.")

# --- FastAPI Application for Frontend ---
app = FastAPI(
    title="LLM Frontend Application",
    description="Serves the web interface for the LLM Interaction App.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None, # Disable docs for the frontend app
    redoc_url=None # Disable redoc for the frontend app
)

# --- Jinja2 Templates and Static Files Configuration ---
# Define the path to your templates directory
templates_dir = os.path.join(os.path.dirname(__file__), 'frontend_app', 'templates')
templates = Jinja2Templates(directory=templates_dir)

# Define the path to your static files directory
static_dir = os.path.join(os.path.dirname(__file__), 'frontend_app', 'static')
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# --- Include the frontend router ---
# This router will define all the HTML-serving routes (e.g., /, /login, /dashboard)
# and ensure they pass the backend_api_url to the templates.
app.include_router(frontend_router)

# Note: No API endpoints are defined directly in this frontend app.py.
# All API calls will be made from frontend JavaScript to the separate backend.
