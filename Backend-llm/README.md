# Backend-llm Service

**TellMeMore LLM API** - Unified LangChain-powered service for OpenAI, Google Gemini, and Groq models with real-time streaming support.

---

## 📚 Documentation

- **[STREAMING_IMPLEMENTATION_PLAN.md](./STREAMING_IMPLEMENTATION_PLAN.md)** - Complete streaming implementation plan
- **[PHASE_1_COMPLETE.md](./PHASE_1_COMPLETE.md)** - Phase 1 completion summary ✅
- **[STREAMING_QUICK_REFERENCE.md](./STREAMING_QUICK_REFERENCE.md)** - Quick reference for streaming
- **[LANGCHAIN_MIGRATION_PLAN.md](./LANGCHAIN_MIGRATION_PLAN.md)** - LangChain migration details (Phase 3 Complete ✅)
- **[backend_llm_api_endpoints.md](./backend_llm_api_endpoints.md)** - API endpoint documentation
- **[tests/CURL_EXAMPLES.md](./tests/CURL_EXAMPLES.md)** - cURL examples for testing

---

## 🚀 Quick Start

### Running the FastAPI Server

```bash
uvicorn api.main:app --reload --port 8001
```

### Testing Streaming Endpoints

```bash
# Quick test with curl
curl -N -X POST http://localhost:8001/chat/openai/gpt-4o/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Count to 5", "session_id": "test-123"}'

# Or use the Python test script
python tests/test_streaming_manual.py test openai gpt-4o
```
