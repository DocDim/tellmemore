# TellMeMore Frontend Application

This repository contains the **frontend application for the _TellMeMore_ project**, built with **FastAPI** for serving HTML templates and static assets. It leverages **Bootstrap 5** and custom **JavaScript** for interactive elements, and communicates with:

- A separate **FastAPI backend API** (for user authentication, chat sessions, and prompt storage)
- A dedicated **LLM API** (for AI model interactions using ChatGPT / OpenAI and Gemini / Google)

---

## Features

**User Authentication:** Login and registration pages.  
**Session Management:** Create new chat sessions and view historical sessions grouped by date.  
**Dual AI Chat Interface:** Send prompts to, and receive responses from, two different LLM providers simultaneously.  
**Conversation History:** Full conversation history displayed for each selected chat session.  
**Responsive Design:** Optimized for all screen sizes using Bootstrap.

---

## Prerequisites

Make sure you have the following installed:

- **Python 3.8+**
- **pip** (Python package installer)

---

## Setup and Installation

1️⃣ **Clone the repository:**

```bash
git clone <your-frontend-repo-url>
cd TELLMEMORE_FRONTEND
```

2️⃣ **Create a Python virtual environment (recommended):**

```bash
python -m venv venv
```

3️⃣ **Activate the virtual environment:**

- On **Windows**:
    ```bash
    .\venv\Scripts\activate
    ```
- On **macOS/Linux**:
    ```bash
    source venv/bin/activate
    ```

4️⃣ **Install dependencies:**

```bash
pip install -r requirements.txt
```

_(Refer to `requirements.txt` for the exact package list.)_

---

##  Configuration

**Create a `.env` file in the root directory:**

```dotenv
# .env file for TELLMEMORE_FRONTEND
FRONTEND_PORT=8080
BACKEND_API_URL="http://127.0.0.1:8000/api/v1"
LLM_API_BASE_URL="http://127.0.0.1:8001"
```

- `FRONTEND_PORT`: Port where the frontend app will run.
- `BACKEND_API_URL`: Base URL for your main backend API (user management, sessions, prompts).
- `LLM_API_BASE_URL`: Base URL for your LLM API (for ChatGPT / Gemini requests).

---

##  Running the Application

Make sure your **backend API** and **LLM API** are already running.  
_(Refer to their respective `README.md` files for setup and execution instructions.)_

Then run the FastAPI frontend:

```bash
uvicorn app:app --reload --port 8080
```

_(Or use the `FRONTEND_PORT` from your `.env` if different.)_

Open your browser and go to:

```
http://127.0.0.1:8080
```

---

## Project Structure

```
TELLMEMORE_FRONTEND/
├── app.py                  # Main FastAPI app serving frontend
├── config.py               # Configuration settings (API URLs, ports)
├── routes.py               # HTML routes (/, /login, /dashboard)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── frontend_app/
    ├── __init__.py
    ├── static/             # CSS, JS, images (e.g. logo.jpg)
    └── templates/          # Jinja2 HTML templates
        ├── base.html
        ├── auth.html       # Login/Registration page
        └── dashboard.html  # Chat dashboard
```

---

## How It Works

- **FastAPI as a Web Server:** Serves static HTML, CSS, JS files like a traditional web server.  
- **Jinja2 Templating:** Injects dynamic values (like API URLs) into HTML templates.  
- **JavaScript Fetch API:** Handles all API requests to the backend & LLM services directly from the browser.
