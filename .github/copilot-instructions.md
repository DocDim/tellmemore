# Copilot Instructions: TellMeMore Project

## Overview

TellMeMore is a modular, multi-service application for interacting with Large Language Models (LLMs) via a secure, user-friendly web interface. The project is designed for extensibility, security, and professional code quality.

## Architecture

- **Backend-da**: FastAPI service for user management, chat sessions, prompts, quotas, and audit logs. Exposes RESTful endpoints for all core data and user operations. Uses SQLAlchemy for database models and JWT for authentication. All user and session data is managed here.
- **Backend-llm**: FastAPI service for querying multiple LLM providers (OpenAI, Google Gemini, Groq LLaMA3). Handles chat history, model selection, and response formatting. **Uses a unified LangChain service (`langchain_service.py`) to interface with all providers (`langchain_openai`, `langchain_google_genai`, `langchain_groq`). This service handles model instantiation, message conversion, and streaming responses.** All LLM requests are routed through this service.
- **Frontend-ui**: FastAPI-based frontend serving HTML via Jinja2 templates (Legacy/Reference). Handles authentication and dashboard UI, with all business logic in backend APIs.
- **Frontend-next**: Next.js 16 frontend, acting as the primary user interface. It features a modern React-based UI and a BFF (Backend-for-Frontend) layer for enhanced security and API mediation. The BFF proxies and validates all API requests, enforces authentication, and prevents direct client access to sensitive backend endpoints.

### Service Interactions

- Frontend-next (React/Next.js) will communicate only with the BFF layer, which then interacts with Backend-da and Backend-llm.
- Backend-da manages users, sessions, prompts, quotas, and audit logs.
- Backend-llm provides LLM responses and model selection.

## Example API Flows

- **User Authentication:**
  1. User logs in via Clerk on Frontend-next.
  2. Frontend includes Clerk session token in requests to BFF.
  3. BFF validates token and forwards request to Backend-da with user context.
- **Chat Session:**
  1. User starts a chat in frontend.
  2. BFF creates session via Backend-da `/api/v1/chat_sessions`.
  3. BFF sends chat prompt to Backend-llm `/chat/{provider}/{model}`.
  4. LLM response is returned and displayed in frontend.

## Environment & Configuration

- All secrets, API URLs, and config values are set via environment variables (see `config.py` and Next.js `.env.local`).
- Never hardcode secrets or sensitive URLs in code or templates.
- Use `.env` files for local development and CI/CD secrets management for production.

## Security Practices

- All sensitive operations (auth, chat, user data) must go through the BFF layer.
- Validate and sanitize all user inputs at both frontend and backend.
- Use secure authentication (JWT, cookies) and authorization checks.
- Never expose backend service URLs directly to the client.
- Use HTTPS for all production deployments.

## Coding Standards

- Use PEP8 for Python and ESLint/Prettier for JavaScript/TypeScript.
- Write modular, well-documented code with clear separation of concerns.
- Prefer async operations and modern Python/JS best practices.
- Include type hints and docstrings for all functions/classes.
- Write unit and integration tests for all major features.
- Handle errors gracefully and log exceptions with context.
- **For Backend-llm, all provider logic is centralized in `langchain_service.py`. Use this unified service for adding new models or providers.**

## Documentation Guidelines

- **Always ask before creating new markdown (.md) files** - Get user confirmation before generating documentation
- **All new documentation must go in the appropriate docs folder:**
  - Project-wide docs → `/docs/`
  - Frontend-next docs → `/frontend-next/docs/`
  - Backend-da docs → `/Backend-da/`
  - Backend-llm docs → `/Backend-llm/`
- **Never create markdown files in the project root** - Keep the root directory clean
- Update the README.md or index files in the docs folders when adding new documentation

## Documentation & Communication

- Keep documentation up to date as goals and architecture evolve.
- Update `.github/copilot-instructions.md` and endpoint docs when major changes occur.
- Notify contributors of significant updates via PRs or project channels.

## Migration Rationale & Outcomes

- Migrating to Next.js 16 enables a modern, scalable frontend with improved developer experience and UI capabilities.
- The BFF layer adds security and flexibility for API mediation.
- Refactoring backend models/code ensures maintainability and professional standards.
- Legacy FastAPI frontend remains for reference; all new development is in Frontend-next.
- **Backend-llm uses a unified LangChain implementation (`langchain_service.py`) for all LLM operations. This provides a consistent interface for streaming and non-streaming requests across different providers (OpenAI, Google, Groq).**

## Documentation Structure

**Project documentation is organized by component:**

- **Project-wide:** [/docs/README.md](../docs/README.md) - Migration plans, Clerk integration, architecture
- **Frontend Next.js:** [/frontend-next/docs/](../frontend-next/docs/) - Chat UI fixes, API integration, phase reports
- **Backend Data API:** [/Backend-da/backend_api_endpoints.md](../Backend-da/backend_api_endpoints.md)
- **Backend LLM API:** [/Backend-llm/backend_llm_api_endpoints.md](../Backend-llm/backend_llm_api_endpoints.md)

## Frontend Migration Documentation

**For all Frontend-next development, follow these migration documents:**

- **Primary Guide:** [docs/frontend-next-migration-plan.md](../docs/frontend-next-migration-plan.md) - Complete implementation roadmap, phases, and timelines
- **Quick Reference:** [docs/MIGRATION-SUMMARY.md](../docs/MIGRATION-SUMMARY.md) - Key decisions, model list, common questions
- **Documentation Index:** [docs/README.md](../docs/README.md) - How to navigate all documentation

**Phases 4-8 Complete ✅ (November 3-5, 2025):**

- **Phase 4 Report:** [frontend-next/docs/PHASE_4_COMPLETE.md](../frontend-next/docs/PHASE_4_COMPLETE.md) - Chat interface implementation
- **Phase 5 Report:** [frontend-next/docs/PHASE_5_COMPLETE.md](../frontend-next/docs/PHASE_5_COMPLETE.md) - Session management and search
- **Phase 6 Report:** [frontend-next/docs/PHASE_6_COMPLETE.md](../frontend-next/docs/PHASE_6_COMPLETE.md) - Prompts library and quota management
- **Phase 7 Report:** [frontend-next/docs/PHASE_7_COMPLETE.md](../frontend-next/docs/PHASE_7_COMPLETE.md) - Settings and user profile
- **Phase 8 Report:** [frontend-next/docs/PHASE_8_COMPLETE.md](../frontend-next/docs/PHASE_8_COMPLETE.md) - Polish & optimization (95% complete)

**What's Working:**

- ✅ Dual chat interface with OpenAI, Google Gemini, and Groq models
- ✅ Markdown and code syntax highlighting
- ✅ Chat history persistence and loading
- ✅ Model selection with command palette
- ✅ Error handling and loading states per model
- ✅ Session title auto-update
- ✅ All internal API endpoints (BFF layer complete)
- ✅ Session CRUD operations (create, delete, rename, load)
- ✅ Session sorting (newest first, backend + frontend)
- ✅ Global search with dropdown (session title search)
- ✅ Keyboard shortcuts (Cmd/Ctrl+K, Cmd/Ctrl+/, Cmd/Ctrl+B, ↑↓, Enter, Esc)
- ✅ Modern dashboard header with breadcrumb navigation
- ✅ Responsive design (mobile-friendly sidebar and search)

**Key Decisions (see migration docs for details):**

- State Management: React Query for backend data, Zustand for UI preferences only
- Caching: "use cache" for Server Components (system prompts, models list), React Query for dynamic data
- Server Actions: Use for all mutations (create session, save prompt, update quota)
- No direct client-to-backend API calls - all requests go through BFF layer

**Chat UI Optimistic Updates ✅ (January 30, 2025):**

The chat interface now features a production-ready optimistic UI with instant message display, smooth streaming responses, and zero flicker. All cache updates are handled manually to avoid race conditions and ensure data consistency.

- **Documentation:** [frontend-next/docs/CHAT_UI_FIXES_README.md](../frontend-next/docs/CHAT_UI_FIXES_README.md) - Complete index of all chat UI fixes
- **Summary:** [frontend-next/docs/CHAT_UI_COMPLETE_SUMMARY.md](../frontend-next/docs/CHAT_UI_COMPLETE_SUMMARY.md) - Full journey from broken to perfect
- **Implementation:** Manual cache updates via `queryClient.setQueryData()`, no automatic invalidations
- **Key Fix:** `refetchOnMount: true` (default) + `staleTime: Infinity` enables cache observation without network requests
- **Result:** Instant user messages, smooth streaming, persistent responses, zero flicker

**Critical Patterns for Chat UI:**

- ✅ Manual cache updates only (no `invalidateQueries` for prompts)
- ✅ Preserve `llm_responses` when replacing temp IDs with backend data
- ✅ Sort messages by timestamp before rendering
- ✅ Use `staleTime: Infinity` to prevent auto-refetch, but keep `refetchOnMount: true` for cache observation
- ❌ Never invalidate chat history cache (causes flicker)
- ❌ Never use automatic optimistic updates (causes duplicates)

## Migration Plan

1. Create this instructions file for LLM and contributor context. (Completed)
2. Refactor and improve backend models and code in Backend-llm. (Completed)
3. **Consolidate Backend-llm provider logic into `langchain_service.py` using `langchain_openai`, `langchain_google_genai`, and `langchain_groq`. (Completed)**
4. Add unit and integration tests for the unified service. (In Progress)
5. Build the Next.js 16 frontend in Frontend-next, using a BFF layer and migrating logic from Frontend-ui. (Completed)

## Key Endpoints

- See `Backend-da/backend_api_endpoints.md` and `Backend-llm/backend_llm_api_endpoints.md` for full API documentation and schemas.
- **Backend-llm API endpoints are powered by `langchain_service.py`.**

## Additional Notes

- Static assets and legacy frontend code will remain in Frontend-ui for reference.
- All new frontend development will occur in Frontend-next.
- For questions or major changes, update this file and notify contributors.
- **Contributors: Use `langchain_service.py` for all LLM interactions.**

## Clerk Authentication Integration

- Clerk is used for authentication and user identity management. All sensitive backend endpoints (users, chat sessions, prompts, audit logs) require Clerk authentication via the `get_current_user_claims` dependency.
- Clerk user ID (from JWT claims) is mapped to an internal user record in Postgres using `get_or_create_user_by_clerk_id`. If the Clerk user does not exist in the DB, a new record is created automatically.
- All business logic and data access is scoped to the authenticated Clerk user. No direct UUIDs from the client are used for user access.
- Environment variables for Clerk integration (`CLERK_SECRET_KEY`, `CLERK_ISSUER_URL`) must be set in `.env`.
- The backend is now secure, scalable, and ready for production use with Clerk and Postgres.

### Example Flow

1. User logs in via Clerk (Next.js frontend).
2. Frontend sends Clerk JWT to backend for API calls.
3. Backend verifies JWT, extracts Clerk user ID, and maps to internal user record.
4. All operations (user, chat, prompt, audit) are performed for the authenticated Clerk user only.

---

This file provides essential context for Copilot, LLMs, and human contributors. Always review and update as the project evolves.
