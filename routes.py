# TELLMEMORE_FRONTEND/routes.py (Frontend HTML Routes)
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from config import settings # Import settings for backend and LLM API URLs

# Initialize Jinja2Templates, pointing to the templates directory
# Ensure this path is correct relative to where routes.py is executed
templates = Jinja2Templates(directory="frontend_app/templates")

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def auth_page(request: Request):
    """
    Serves the authentication (login/register) page as the default root.
    """
    # Pass both backend and LLM API URLs to the template
    print(f"DEBUG (frontend routes.py): backend_api_url being passed to auth.html: {settings.BACKEND_API_URL}")
    print(f"DEBUG (frontend routes.py): llm_api_base_url being passed to auth.html: {settings.LLM_API_BASE_URL}")
    return templates.TemplateResponse(
        "auth.html",
        {
            "request": request,
            "backend_api_url": settings.BACKEND_API_URL,
            "llm_api_base_url": settings.LLM_API_BASE_URL # Pass LLM API URL
        }
    )

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Serves the authentication (login/register) page.
    """
    # Pass both backend and LLM API URLs to the template
    print(f"DEBUG (frontend routes.py): backend_api_url being passed to auth.html: {settings.BACKEND_API_URL}")
    print(f"DEBUG (frontend routes.py): llm_api_base_url being passed to auth.html: {settings.LLM_API_BASE_URL}")
    return templates.TemplateResponse(
        "auth.html",
        {
            "request": request,
            "backend_api_url": settings.BACKEND_API_URL,
            "llm_api_base_url": settings.LLM_API_BASE_URL # Pass LLM API URL
        }
    )

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """
    Serves a registration page (reusing auth.html).
    """
    # Pass both backend and LLM API URLs to the template
    print(f"DEBUG (frontend routes.py): backend_api_url being passed to auth.html: {settings.BACKEND_API_URL}")
    print(f"DEBUG (frontend routes.py): llm_api_base_url being passed to auth.html: {settings.LLM_API_BASE_URL}")
    return templates.TemplateResponse(
        "auth.html",
        {
            "request": request,
            "is_register": True,
            "backend_api_url": settings.BACKEND_API_URL,
            "llm_api_base_url": settings.LLM_API_BASE_URL # Pass LLM API URL
        }
    )

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """
    Serves the protected dashboard page.
    """
    # Pass both backend and LLM API URLs to the template
    print(f"DEBUG (frontend routes.py): backend_api_url being passed to dashboard.html: {settings.BACKEND_API_URL}")
    print(f"DEBUG (frontend routes.py): llm_api_base_url being passed to dashboard.html: {settings.LLM_API_BASE_URL}")
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "backend_api_url": settings.BACKEND_API_URL,
            "llm_api_base_url": settings.LLM_API_BASE_URL # Pass LLM API URL
        }
    )
