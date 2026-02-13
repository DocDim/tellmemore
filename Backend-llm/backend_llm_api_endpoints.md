# Backend LLM API Endpoints Reference

Complete API documentation for TellMeMore Backend-llm service.

This document provides comprehensive details on all LLM backend endpoints, including chat endpoints for multiple providers and dynamic model discovery endpoints. All chat endpoints now use the unified LangChain framework with automatic LangSmith observability.

**Last Updated:** February 10, 2026  
**API Version:** 0.1  
**Base URL:** `http://localhost:8001` (development) | `https://backend-llm.your-domain.com` (production)

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Chat Endpoints](#-chat-endpoints)
3. [Model Discovery Endpoints](#-model-discovery-endpoints)
4. [Request & Response Schemas](#-request--response-schemas)
5. [Usage Examples](#-usage-examples)
6. [Frontend Integration](#-frontend-integration)
7. [LangChain Migration](#-langchain-migration)

---

## 🎯 Overview

Backend-llm provides:

- **Chat endpoints** for OpenAI, Google Gemini, and Groq models
- **Model discovery** endpoints for dynamic model listing
- **Unified LangChain service** with automatic LangSmith tracing
- **Multi-turn conversations** with chat history support
- **System prompts** for custom instructions
- **Token usage tracking** across all providers

### Key Features

✅ **Unified Architecture** - All providers use the same LangChain service  
✅ **Automatic Observability** - LangSmith tracing built-in (when enabled)  
✅ **Dynamic Model Lists** - Real-time model fetching from provider APIs  
✅ **Production-Ready** - Error handling, validation, CORS support  
✅ **Type-Safe** - Pydantic models with full validation  

---

## 💬 Chat Endpoints

All chat endpoints follow the same pattern and support the same features:

- Multi-turn conversations via `chat_history`
- System prompts for custom instructions
- Session tracking via `session_id`
- Automatic token usage tracking
- LangSmith tracing (when `LANGSMITH_TRACING=true`)

### 1. OpenAI Chat

**Endpoint:** `POST /chat/openai/{model_name}`

**Supported Models:**

- `gpt-4o`, `gpt-4o-mini` - High-intelligence flagship models
- `o1`, `o1-mini`, `o3-mini` - Advanced reasoning models
- `gpt-5` series - Next-generation models (if available)

**Example Request:**

```bash
curl -X POST http://localhost:8001/chat/openai/gpt-4o \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain quantum computing in simple terms",
    "session_id": "user-session-123",
    "chat_history": [],
    "system_prompts": ["You are a helpful physics tutor"]
  }'
```

**Response:**

```json
{
  "answer": "Quantum computing uses quantum mechanics...",
  "raw_response": {...},
  "error_message": null,
  "session_id": "user-session-123",
  "model": "gpt-4o",
  "provider": "openai",
  "request_timestamp": "2026-02-10T12:00:00Z",
  "response_timestamp": "2026-02-10T12:00:02Z",
  "latency_ms": 2000,
  "usage": {
    "completion_tokens": 150,
    "prompt_tokens": 25,
    "total_tokens": 175
  }
}
```

---

### 2. Google Gemini Chat

**Endpoint:** `POST /chat/google/{model_name}`

**Supported Models:**

- `gemini-2.0-flash`, `gemini-2.0-flash-lite` - Fast, production-ready models
- `gemini-2.5-pro`, `gemini-2.5-flash` - Advanced reasoning
- `gemini-3` series - Next-generation models (if available)

**Example Request:**

```bash
curl -X POST http://localhost:8001/chat/google/gemini-2.0-flash \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the benefits of renewable energy?",
    "session_id": "session-456"
  }'
```

**Response:** Same format as OpenAI (see above)

---

### 3. Groq LLaMA Chat

**Endpoint:** `POST /chat/groq/{model_name}`

**Supported Models:**

- `llama-3.3-70b-versatile` - High performance
- `llama-3.1-8b-instant` - Ultra-fast inference

**Example Request:**

```bash
curl -X POST http://localhost:8001/chat/groq/llama-3.3-70b-versatile \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Write a haiku about coding",
    "session_id": "creative-session"
  }'
```

**Response:** Same format as OpenAI (see above)

---

## 🔍 Model Discovery Endpoints

Dynamic endpoints that fetch available models in real-time from each provider's API. **No more hardcoded model lists!**

### 1. Get All Models

**Endpoint:** `GET /models`

**Description:** Fetch available **flagship** models from OpenAI, Google Gemini, and Groq. Uses strict filtering to exclude legacy, preview, and specialized variants, ensuring a clean list of high-quality models.

**Example Request:**

```bash
curl http://localhost:8001/models
```

**Response:**

```json
{
  "success": true,
  "models": {
    "openai": [
      {
        "id": "gpt-4o",
        "name": "gpt-4o",
        "provider": "openai",
        "created": 1700000000,
        "owned_by": "openai"
      },
      {
        "id": "o1-mini",
        "name": "o1-mini",
        "provider": "openai",
        "created": 1700000001,
        "owned_by": "openai"
      }
      // ... ~10 flagship models
    ],
    "google": [
      {
        "id": "gemini-2.0-flash",
        "name": "gemini-2.0-flash",
        "provider": "google",
        "display_name": "Gemini 2.0 Flash",
        "description": "Fast multimodal model",
        "supported_methods": ["generateContent", "streamGenerateContent"]
      }
      // ... ~7 flagship models
    ],
    "groq": [
      {
        "id": "llama-3.3-70b-versatile",
        "name": "llama-3.3-70b-versatile",
        "provider": "groq",
        "created": 1700000002,
        "owned_by": "Meta",
        "active": true
      }
      // ... ~2 flagship models
    ]
  },
  "total_count": {
    "openai": 11,
    "google": 7,
    "groq": 2
  }
}
```

**Use Case:** Display all available models in an admin panel or debug view.

---

### 2. Get Featured Models

**Endpoint:** `GET /models/featured`

**Description:** Get a curated list of recommended models for each provider (hardcoded, fast).

**Example Request:**

```bash
curl http://localhost:8001/models/featured
```

**Response:**

```json
{
  "success": true,
  "featured_models": {
    "openai": [
      {
        "id": "gpt-5",
        "name": "GPT-5",
        "description": "Most capable model"
      },
      {
        "id": "gpt-5-mini",
        "name": "GPT-5 Mini",
        "description": "Fast and affordable"
      },
      {
        "id": "gpt-nano",
        "name": "GPT Nano",
        "description": "Ultra-fast responses"
      }
    ],
    "google": [
      {
        "id": "gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "description": "Most advanced reasoning"
      },
      {
        "id": "gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "description": "Fast multimodal model"
      },
      {
        "id": "gemini-2.5-flash-lite",
        "name": "Gemini 2.5 Flash Lite",
        "description": "Lightweight model"
      }
    ],
    "groq": [
      {
        "id": "llama-3.3-70b-versatile",
        "name": "LLaMA 3.3 70B",
        "description": "High performance"
      },
      {
        "id": "llama-3.1-8b-instant",
        "name": "LLaMA 3.1 8B",
        "description": "Ultra-fast inference"
      }
    ]
  }
}
```

**Use Case:** Populate model selection dropdowns in the frontend (faster than `/models`, doesn't require API calls to providers).

---

### 3. Get Provider-Specific Models

**Endpoint:** `GET /models/{provider}`

**Path Parameters:**

- `provider` - One of: `openai`, `google`, `groq`

**Example Request:**

```bash
curl http://localhost:8001/models/groq
```

**Response:**

```json
{
  "success": true,
  "provider": "groq",
  "models": [
    {
      "id": "llama-3.3-70b-versatile",
      "name": "llama-3.3-70b-versatile",
      "provider": "groq",
      "created": 1700000002,
      "owned_by": "Meta",
      "active": true
    },
    {
      "id": "llama-3.1-8b-instant",
      "name": "llama-3.1-8b-instant",
      "provider": "groq",
      "created": 1700000003,
      "owned_by": "Meta",
      "active": true
    }
    // ... more Groq models
  ],
  "count": 2
}
```

**Use Case:** Fetch models for a specific provider when building provider-specific UI.

---

## 📝 Request & Response Schemas

### Chat Request: `SingleModelChatRequest`

```python
class SingleModelChatRequest(BaseModel):
    question: str  # Required: The user's question/prompt
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    chat_history: Optional[List[ChatMessageAPI]] = Field(default_factory=list)
    system_prompts: Optional[List[str]] = Field(default_factory=list)
    extra_params: Optional[Dict[str, Any]] = {}  # temperature, max_tokens, etc.
```

**Fields:**

- `question` *(required)*: The user's message
- `session_id` *(optional)*: Session identifier for tracking conversations (auto-generated if not provided)
- `chat_history` *(optional)*: Previous messages in the conversation
- `system_prompts` *(optional)*: System instructions (e.g., "You are a helpful assistant")
- `extra_params` *(optional)*: Model-specific parameters (temperature, max_tokens, etc.)

---

### Chat History Message: `ChatMessageAPI`

```python
class ChatMessageAPI(BaseModel):
    role: str  # "user", "assistant", "system", "human", "ai"
    content: str
```

**Example:**

```json
{
  "role": "user",
  "content": "What is machine learning?"
}
```

---

### Chat Response: `QueryResponse`

```python
class QueryResponse(BaseModel):
    answer: Optional[str] = None
    raw_response: Optional[Any] = None
    error_message: Optional[str] = None
    session_id: str
    model: ModelName
    provider: ModelProvider
    request_timestamp: datetime
    response_timestamp: datetime
    latency_ms: float
    usage: Optional[Dict[str, Any]] = None  # Token usage stats
```

**Fields:**

- `answer`: The LLM's response text
- `raw_response`: Full response object from LangChain
- `error_message`: Error details (null if successful)
- `session_id`: Session identifier
- `model`: Model name used
- `provider`: Provider name ("openai", "google", "groq")
- `request_timestamp`: When request was received
- `response_timestamp`: When response was sent
- `latency_ms`: Response time in milliseconds
- `usage`: Token usage statistics (varies by provider)

---

### Model Enums

#### ModelName

```python
class ModelName(str, Enum):
    # OpenAI Models
    GPT_4O = "gpt-4o"
    O1_MINI = "o1-mini"
    
    # Google Gemini Models
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    
    # Groq LLaMA Models
    LLAMA_3_3_70B_VERSATILE = "llama-3.3-70b-versatile"
    LLAMA_3_1_8B_INSTANT = "llama-3.1-8b-instant"
```

#### ModelProvider

```python
class ModelProvider(str, Enum):
    OPENAI = "openai"
    GOOGLE = "google"
    GROQ = "groq"
```

---

## 💡 Usage Examples

### Simple Chat (No History)

```bash
curl -X POST http://localhost:8001/chat/openai/gpt-5-mini \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is 2+2?"
  }'
```

---

### Multi-Turn Conversation

```bash
curl -X POST http://localhost:8001/chat/google/gemini-2.5-flash \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What was my previous question?",
    "session_id": "conv-123",
    "chat_history": [
      {"role": "user", "content": "Tell me about Python"},
      {"role": "assistant", "content": "Python is a high-level programming language..."}
    ]
  }'
```

---

### With System Prompts

```bash
curl -X POST http://localhost:8001/chat/groq/llama-3.3-70b-versatile \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Calculate 15 * 23",
    "system_prompts": [
      "You are a math tutor. Always show your work step by step."
    ]
  }'
```

---

### With Extra Parameters

```bash
curl -X POST http://localhost:8001/chat/openai/gpt-5 \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Write a creative story",
    "extra_params": {
      "temperature": 0.9,
      "max_tokens": 500
    }
  }'
```

---

## 🌐 Frontend Integration

### Next.js BFF Layer (Recommended)

The frontend should **not** call Backend-llm directly. Instead, use the BFF (Backend-for-Frontend) layer:

**File:** `frontend-next/app/api/backend-llm/chat/route.ts`

```typescript
// Frontend calls BFF
// Frontend calls BFF
const response = await fetch('/api/backend-llm/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "Hello!",
    model: "gpt-5",
    provider: "openai"
  })
});

const data = await response.json();
```

**BFF then proxies to Backend-llm:**

```typescript
// BFF proxies to Backend-llm
const llmResponse = await fetch(
  `${env.server.backendLlmUrl}/chat/${provider}/${model}`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, chat_history, session_id })
  }
);
```

---

### Model Selection Dropdown

Use the `/models/featured` endpoint to populate model dropdowns:

```typescript
// Fetch featured models on component mount
useEffect(() => {
  const fetchModels = async () => {
    const response = await fetch('/api/backend-llm/models/featured');
    const { featured_models } = await response.json();
    
    setOpenAIModels(featured_models.openai);
    setGeminiModels(featured_models.google);
    setGroqModels(featured_models.groq);
  };
  
  fetchModels();
}, []);
```

---

### Dual Chat Interface

For side-by-side model comparison (current TellMeMore UI):

```typescript
// Send parallel requests to different models
const [leftResponse, rightResponse] = await Promise.all([
  fetch('/api/backend-llm/chat', {
    method: 'POST',
    body: JSON.stringify({
      question: userMessage,
      model: "gpt-5",
      provider: "openai"
    })
  }),
  fetch('/api/backend-llm/chat', {
    method: 'POST',
    body: JSON.stringify({
      question: userMessage,
      model: "gemini-2.5-flash",
      provider: "google"
    })
  })
]);

// Display responses side by side
```

---

## 🚀 LangChain Migration

**Status:** ✅ Complete (February 10, 2026)

All chat endpoints now use a unified LangChain service instead of direct provider SDKs.

### What Changed

**Before (Direct SDKs):**

```python
# 3 separate service files
from api.services.openai_service import chat_with_model
from api.services.google_gemini_service import chat_with_model
from api.services.groq_service import chat_with_model
```

**After (Unified LangChain):**

```python
# 1 unified service
from api.services.langchain_service import chat_with_model

# All endpoints use the same function
result = await chat_with_model(
    provider="openai",  # or "google", "groq"
    model_name="gpt-5",
    messages=messages
)
```

### Benefits

✅ **Unified Codebase** - 1 service instead of 3  
✅ **Automatic Tracing** - LangSmith observability built-in  
✅ **Standardized Responses** - Same format across all providers  
✅ **Easy to Extend** - Add new providers with 1-2 lines of code  
✅ **Better Testing** - Use LangChain test utilities  

### LangSmith Observability

When `LANGSMITH_TRACING=true` in `.env`, all LLM calls are automatically traced:

- **Request/Response Logging** - Full input/output capture
- **Token Tracking** - Automatic usage monitoring
- **Performance Metrics** - Latency, throughput, error rates
- **Debugging Tools** - Trace replay, comparison, A/B testing

View traces at: <https://smith.langchain.com>

### Migration Documentation

- **Full Migration Plan:** [LANGCHAIN_MIGRATION_PLAN.md](LANGCHAIN_MIGRATION_PLAN.md)
- **Test Results:** All 3 providers verified working
- **Breaking Changes:** None (API contracts preserved)

---

## 📚 Related Documentation

### Frontend Integration

- **Phase 4 Complete:** [frontend-next/docs/PHASE_4_COMPLETE.md](../frontend-next/docs/PHASE_4_COMPLETE.md) - Dual chat interface completion
- **Chat Data Flow:** [frontend-next/docs/CHAT_DATA_FLOW_VERIFICATION.md](../frontend-next/docs/CHAT_DATA_FLOW_VERIFICATION.md) - End-to-end flow
- **BFF Layer:** [frontend-next/app/api/backend-llm/chat/route.ts](../frontend-next/app/api/backend-llm/chat/route.ts) - Next.js BFF proxy

### Migration Guides

- **LangChain Migration:** [LANGCHAIN_MIGRATION_PLAN.md](LANGCHAIN_MIGRATION_PLAN.md) - Complete migration guide
- **Frontend Migration:** [../docs/frontend-next-migration-plan.md](../docs/frontend-next-migration-plan.md) - Next.js 16 migration
- **Quick Reference:** [../docs/MIGRATION-SUMMARY.md](../docs/MIGRATION-SUMMARY.md) - Model list and decisions

---

## 🔧 Development

### Local Testing

```bash
# Start Backend-llm
cd Backend-llm
source ../.venv/bin/activate
uvicorn api.main:app --reload --port 8001

# Test chat endpoint
curl -X POST http://localhost:8001/chat/openai/gpt-5-mini \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello!"}'

# Test model discovery
curl http://localhost:8001/models/featured
```

### Environment Variables

Required in `.env`:

```env
# Provider API Keys
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIza...
GROQ_API_KEY=gsk_...

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# LangSmith (Optional)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=tellmemore-backend-llm
```

---

## 🎯 Summary

Backend-llm provides:

**Chat Endpoints:**

- `POST /chat/openai/{model}` - OpenAI GPT models
- `POST /chat/google/{model}` - Google Gemini models
- `POST /chat/groq/{model}` - Groq LLaMA models

**Model Discovery:**

- `GET /models` - All available models (real-time)
- `GET /models/featured` - Curated recommended models
- `GET /models/{provider}` - Provider-specific models

**Features:**

- ✅ Unified LangChain service
- ✅ Automatic LangSmith tracing
- ✅ Multi-turn conversations
- ✅ System prompts support
- ✅ Token usage tracking
- ✅ Dynamic model discovery

**Ready for production!** 🚀

---

**Questions?** Open an issue or contact the development team.
