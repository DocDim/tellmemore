# Streaming Endpoints - cURL Examples

Quick reference for testing streaming endpoints using curl.

---

## Prerequisites

```bash
# Make sure Backend-llm is running
cd Backend-llm
uvicorn api.main:app --reload --port 8001
```

---

## Basic Streaming Requests

### OpenAI Streaming

```bash
curl -N -X POST http://localhost:8001/chat/openai/gpt-4o/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Count to 5",
    "session_id": "test-123"
  }'
```

### Google Gemini Streaming

```bash
curl -N -X POST http://localhost:8001/chat/google/gemini-2.5-flash/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Say hello",
    "session_id": "test-123"
  }'
```

### Groq LLaMA Streaming

```bash
curl -N -X POST http://localhost:8001/chat/groq/llama-3.3-70b-versatile/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the capital of France?",
    "session_id": "test-123"
  }'
```

**Note:** The `-N` flag disables buffering for real-time output.

---

## Advanced Examples

### With Chat History

```bash
curl -N -X POST http://localhost:8001/chat/openai/gpt-4o/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is my name?",
    "session_id": "test-conversation",
    "chat_history": [
      {"role": "user", "content": "My name is Alice"},
      {"role": "assistant", "content": "Hello Alice!"}
    ]
  }'
```

### With System Prompts

```bash
curl -N -X POST http://localhost:8001/chat/openai/gpt-4o/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Is the sky blue?",
    "session_id": "test-system",
    "system_prompts": ["You are a helpful assistant that responds concisely."]
  }'
```

### Save Stream to File

```bash
curl -N -X POST http://localhost:8001/chat/openai/gpt-4o/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Write a haiku about coding",
    "session_id": "test-save"
  }' > stream_output.txt
```

---

## Expected Output Format

### SSE Event Stream

```
data: {"token": "Hello", "chunk_type": "content", "done": false}

data: {"token": " world", "chunk_type": "content", "done": false}

data: {"token": "!", "chunk_type": "content", "done": false}

data: {"token": "", "chunk_type": "final", "done": true, "full_content": "Hello world!", "usage": {...}}
```

### Parsing with jq

```bash
# Extract only tokens
curl -N -X POST http://localhost:8001/chat/openai/gpt-4o/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Say hello", "session_id": "test"}' | \
  grep "^data:" | \
  sed 's/^data: //' | \
  jq -r '.token // empty'

# Extract final content
curl -s -X POST http://localhost:8001/chat/openai/gpt-4o/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Say hello", "session_id": "test"}' | \
  grep "^data:" | \
  sed 's/^data: //' | \
  jq -r 'select(.done == true) | .full_content'
```

---

## Comparing Streaming vs Non-Streaming

### Non-Streaming (Legacy)

```bash
time curl -X POST http://localhost:8001/chat/openai/gpt-4o \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the capital of France?",
    "session_id": "test-compare"
  }' | jq '.answer'
```

### Streaming

```bash
time curl -N -X POST http://localhost:8001/chat/openai/gpt-4o/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the capital of France?",
    "session_id": "test-compare-stream"
  }'
```

---

## Error Handling

### Invalid Model (should return 400)

```bash
curl -N -X POST http://localhost:8001/chat/openai/gemini-2.5-flash/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Test",
    "session_id": "test-error"
  }'
```

### Missing Required Field (should return 422)

```bash
curl -N -X POST http://localhost:8001/chat/openai/gpt-4o/stream \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-error"
  }'
```

---

## Performance Testing

### Measure Time to First Token (TTFT)

```bash
# Using httpie for better timing display
http --stream POST localhost:8001/chat/openai/gpt-4o/stream \
  question="Count to 10" \
  session_id="perf-test"
```

### Concurrent Streaming (Dual-Chat Simulation)

```bash
# Terminal 1
curl -N -X POST http://localhost:8001/chat/openai/gpt-4o/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Tell me a joke", "session_id": "dual-1"}' &

# Terminal 2
curl -N -X POST http://localhost:8001/chat/google/gemini-2.5-flash/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Tell me a joke", "session_id": "dual-2"}' &

wait
```

---

## Debugging Tips

### View Headers

```bash
curl -N -v -X POST http://localhost:8001/chat/openai/gpt-4o/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Test", "session_id": "debug"}' \
  2>&1 | grep -E "^< |^data:"
```

**Expected Headers:**
- `< content-type: text/event-stream; charset=utf-8`
- `< cache-control: no-cache`
- `< x-accel-buffering: no`

### Test All Models

```bash
#!/bin/bash
# Test all supported models

models=(
  "openai/gpt-4o"
  "openai/gpt-4o-mini"
  "openai/gpt-nano"
  "google/gemini-2.5-pro"
  "google/gemini-2.5-flash"
  "google/gemini-2.5-flash-lite"
  "groq/llama-3.3-70b-versatile"
  "groq/llama-3.1-8b-instant"
)

for model in "${models[@]}"; do
  provider="${model%%/*}"
  model_name="${model##*/}"
  
  echo "Testing $provider/$model_name..."
  
  curl -s -N -X POST "http://localhost:8001/chat/$provider/$model_name/stream" \
    -H "Content-Type: application/json" \
    -d "{\"question\": \"Say hello\", \"session_id\": \"test-$model_name\"}" | \
    head -n 5
  
  echo -e "\n---\n"
done
```

---

## API Documentation

Access Swagger UI for interactive testing:

```bash
# Open in browser
open http://localhost:8001/docs

# Or view JSON schema
curl http://localhost:8001/openapi.json | jq
```

---

## Troubleshooting

### No Output Visible

**Problem:** curl buffers output  
**Solution:** Use `-N` flag to disable buffering

```bash
curl -N -X POST http://localhost:8001/chat/openai/gpt-4o/stream ...
```

### Empty Response

**Problem:** Missing API keys  
**Solution:** Check `.env` file has valid keys

```bash
# Backend-llm/.env
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
GROQ_API_KEY=...
```

### CORS Error (when testing from browser)

**Problem:** CORS not configured for your origin  
**Solution:** Add origin to `CORS_ORIGINS` in Backend-llm

```bash
# Backend-llm/.env
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

---

**Documentation:** See [STREAMING_IMPLEMENTATION_PLAN.md](../STREAMING_IMPLEMENTATION_PLAN.md) for full implementation details.
