"""
Integration Tests for Streaming Endpoints
Tests the FastAPI /stream endpoints for all providers
"""

import pytest
from httpx import AsyncClient, ASGITransport
import json
from typing import List, Dict

from api.main import app


@pytest.mark.asyncio
async def test_openai_streaming_endpoint():
    """Test OpenAI streaming endpoint returns SSE events."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "question": "Say 'hello' only",
            "session_id": "test-session-123"
        }
        
        response = await client.post(
            "/chat/openai/gpt-4o/stream",
            json=payload,
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Parse SSE events
        events = []
        content = response.text
        lines = content.strip().split('\n')
        
        for line in lines:
            if line.startswith('data: '):
                event_data = json.loads(line[6:])  # Remove 'data: ' prefix
                events.append(event_data)
        
        # Assertions
        assert len(events) > 0, "Should receive at least one event"
        assert events[-1]["done"] == True, "Last event should have done=True"
        assert "full_content" in events[-1], "Last event should contain full_content"


@pytest.mark.asyncio
async def test_google_streaming_endpoint():
    """Test Google Gemini streaming endpoint returns SSE events."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "question": "Say 'hello' only",
            "session_id": "test-session-123"
        }
        
        response = await client.post(
            "/chat/google/gemini-2.5-flash/stream",
            json=payload,
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Parse SSE events
        events = []
        content = response.text
        lines = content.strip().split('\n')
        
        for line in lines:
            if line.startswith('data: '):
                event_data = json.loads(line[6:])
                events.append(event_data)
        
        # Assertions
        assert len(events) > 0, "Should receive at least one event"
        assert events[-1]["done"] == True, "Last event should have done=True"


@pytest.mark.asyncio
async def test_groq_streaming_endpoint():
    """Test Groq streaming endpoint returns SSE events."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "question": "Say 'hello' only",
            "session_id": "test-session-123"
        }
        
        response = await client.post(
            "/chat/groq/llama-3.3-70b-versatile/stream",
            json=payload,
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Parse SSE events
        events = []
        content = response.text
        lines = content.strip().split('\n')
        
        for line in lines:
            if line.startswith('data: '):
                event_data = json.loads(line[6:])
                events.append(event_data)
        
        # Assertions
        assert len(events) > 0, "Should receive at least one event"
        assert events[-1]["done"] == True, "Last event should have done=True"


@pytest.mark.asyncio
async def test_streaming_with_chat_history():
    """Test streaming endpoint with chat history."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "question": "What is my name?",
            "session_id": "test-session-123",
            "chat_history": [
                {"role": "user", "content": "My name is Alice"},
                {"role": "assistant", "content": "Hello Alice!"}
            ]
        }
        
        response = await client.post(
            "/chat/openai/gpt-4o/stream",
            json=payload,
        )
        
        assert response.status_code == 200
        
        # Parse events
        events = []
        for line in response.text.strip().split('\n'):
            if line.startswith('data: '):
                events.append(json.loads(line[6:]))
        
        # Should complete successfully
        assert events[-1]["done"] == True
        # Response should mention Alice
        full_content = events[-1].get("full_content", "").lower()
        assert "alice" in full_content


@pytest.mark.asyncio
async def test_streaming_with_system_prompts():
    """Test streaming endpoint with system prompts."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "question": "Is the sky blue?",
            "session_id": "test-session-123",
            "system_prompts": ["You are a helpful assistant that responds concisely."]
        }
        
        response = await client.post(
            "/chat/openai/gpt-4o/stream",
            json=payload,
        )
        
        assert response.status_code == 200
        
        # Parse events
        events = []
        for line in response.text.strip().split('\n'):
            if line.startswith('data: '):
                events.append(json.loads(line[6:]))
        
        # Should complete successfully
        assert events[-1]["done"] == True
        assert "full_content" in events[-1]


@pytest.mark.asyncio
async def test_streaming_invalid_model():
    """Test streaming endpoint with invalid model name."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "question": "Hello",
            "session_id": "test-session-123"
        }
        
        # Try to use Google model on OpenAI endpoint
        response = await client.post(
            "/chat/openai/gemini-2.5-flash/stream",
            json=payload,
        )
        
        # Should return 422 (validation error) or 400 (bad request)
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_streaming_sse_format():
    """Test that SSE events are properly formatted."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "question": "Count to 3",
            "session_id": "test-session-123"
        }
        
        response = await client.post(
            "/chat/openai/gpt-4o/stream",
            json=payload,
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Check SSE format
        lines = content.strip().split('\n')
        for line in lines:
            if line.startswith('data: '):
                # Should be valid JSON
                json_str = line[6:]
                event_data = json.loads(json_str)
                
                # Check structure
                assert isinstance(event_data, dict)
                if event_data.get("chunk_type") == "content":
                    assert "token" in event_data
                    assert "done" in event_data
                    assert event_data["done"] == False
                elif event_data.get("done") == True:
                    assert "chunk_type" in event_data


@pytest.mark.asyncio
async def test_streaming_headers():
    """Test that streaming response has correct headers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "question": "Hello",
            "session_id": "test-session-123"
        }
        
        response = await client.post(
            "/chat/openai/gpt-4o/stream",
            json=payload,
        )
        
        # Check headers
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        assert response.headers["cache-control"] == "no-cache"
        assert response.headers["x-accel-buffering"] == "no"


@pytest.mark.asyncio
async def test_non_streaming_still_works():
    """Test that non-streaming endpoints still work (backward compatibility)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "question": "Say 'hello'",
            "session_id": "test-session-123"
        }
        
        # Call non-streaming endpoint
        response = await client.post(
            "/chat/openai/gpt-4o",  # No /stream suffix
            json=payload,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return QueryResponse format (not SSE)
        assert "answer" in data
        assert "session_id" in data
        assert "model" in data
        assert data["session_id"] == "test-session-123"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
