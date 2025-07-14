
# TellMeMore Backend API

This repository contains the **main backend API for the _TellMeMore_ project**, built with **FastAPI**. It handles:

- User authentication & management
- Chat session creation & retrieval
- Prompt storage
- Audit logging

This API is designed to be **separate from the frontend application** and a **dedicated LLM API**.

---

## Features

**User Management:** Register, authenticate, and retrieve user profiles.  
**Authentication:** JWT-based authentication using `passlib` for password hashing and `python-jose` for JWT handling.  
**Chat Session Management:** Create and retrieve chat sessions associated with users.  
**Prompt Storage:** Store user prompts and corresponding LLM responses within chat sessions.  
**Quota Management:** Basic daily quota tracking for users (foundation in place, not fully enforced yet).  
**Audit Logging:** Records user actions for auditing purposes.  
**PostgreSQL Integration:** Uses SQLAlchemy ORM for database operations.  
**CORS Enabled:** Configured to allow cross-origin requests from specified frontend origins.

---

## 🛠 Prerequisites

Make sure you have the following installed:

- **Python 3.8+**
- **pip** (Python package installer)
- **A running PostgreSQL database instance**

---

## Setup and Installation

### 1️⃣ Clone the repository

```bash
git clone <your-backend-repo-url>
cd TELLMEMORE_BACKEND
```

### 2️⃣ Create a Python virtual environment (recommended)

```bash
python -m venv venv
```

### 3️⃣ Activate the virtual environment

- On **Windows**:
    ```bash
    .\venv\Scripts\activate
    ```
- On **macOS/Linux**:
    ```bash
    source venv/bin/activate
    ```

### 4️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

_(Refer to `requirements.txt` for the exact package list.)_

---

## PostgreSQL Setup

- Ensure your PostgreSQL server is running.
- Use the provided SQL script (`postgres-db-script.sql` if included) to create the necessary tables.  
- Connect to your database (via `psql` or any client) and execute the SQL commands.

---

## Configuration

Create a `.env` file in the root of your backend directory:

```dotenv
# .env file for TELLMEMORE_BACKEND
DATABASE_URL="postgresql://user:password@host:port/database_name"
SECRET_KEY="your-very-secret-and-random-key-here-change-this-for-production"
CORS_ORIGINS="http://localhost:8080,http://127.0.0.1:8080"
```

- `DATABASE_URL`: Your PostgreSQL connection string. Replace `user`, `password`, `host`, `port`, and `database_name` with your actual credentials.
- `SECRET_KEY`: A strong, random string used for signing JWT tokens.  
  **IMPORTANT:** Change this to a unique, secure value in production!
- `CORS_ORIGINS`: A comma-separated list of allowed origins (ensure this includes your frontend app URL).

---

## Running the Application

Start the FastAPI backend server:

```bash
uvicorn app:app --reload --port 8000
```

_(Or use another port, but remember to update `BACKEND_API_URL` in your frontend `.env` accordingly.)_

---

## Access the API Docs (Swagger UI)

Once running, navigate to:

```
http://127.0.0.1:8000/api/v1/docs
```

This provides an interactive interface to explore and test your API endpoints.

---

## Project Structure

```
TELLMEMORE_BACKEND/
├── app.py                  # Main FastAPI app
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── backendApp/
    ├── __init__.py
    ├── api/                # Routers for API endpoints
    │   ├── __init__.py
    │   ├── audit_logs.py
    │   ├── auth.py
    │   ├── chat_sessions.py
    │   ├── prompts.py
    │   └── users.py
    ├── dependencies.py     # DB session dependency
    ├── models/             # SQLAlchemy ORM models
    │   ├── __init__.py
    │   └── postgres_models.py
    ├── schemas/            # Pydantic schemas
    │   ├── __init__.py
    │   ├── audit_log_schemas.py
    │   ├── auth_schemas.py
    │   ├── chat_session_schemas.py
    │   ├── prompt_schemas.py
    │   ├── quota_schemas.py
    │   └── user_schemas.py
    └── services/           # Business logic
        ├── __init__.py
        ├── auth_service.py
        ├── chat_session_service.py
        ├── prompt_service.py
        ├── quota_service.py
        └── user_service.py
```

---
