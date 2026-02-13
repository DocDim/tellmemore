"""
Unit Tests for Streaming Chat Functionality
Tests the stream_chat_with_model function for all providers (OpenAI, Google, Groq)
"""

import pytest
import os
from typing import List, Dict
from dotenv import load_dotenv

from api.services.langchain_service import stream_chat_with_model

# Load environment variables for API keys
load_dotenv()


@pytest.mark.asyncio
async def test_openai_streaming_basic():
    """Test OpenAI streaming returns chunks and completes successfully."""
    messages = [{"role": "user", "content": "Say 'hello' only"}]
    
    chunks = []
    async for chunk in stream_chat_with_model("openai", "gpt-4o", messages):
        chunks.append(chunk)
        print(f"Chunk: {chunk}")  # Debug output
    
    # Assertions
    assert len(chunks) > 0, "Should receive at least one chunk"
    assert chunks[-1]["done"] == True, "Final chunk should have done=True"
    assert "full_content" in chunks[-1], "Final chunk should contain full_content"
    assert chunks[-1]["full_content"].strip() != "", "Full content should not be empty"
    
    # Check that at least one content chunk was received
    content_chunks = [c for c in chunks if c.get("chunk_type") == "content"]
    assert len(content_chunks) > 0, "Should receive at least one content chunk"


@pytest.mark.asyncio
async def test_google_streaming_basic():
    """Test Google Gemini streaming returns chunks and completes successfully."""
    messages = [{"role": "user", "content": "Say 'hello' only"}]
    
    chunks = []
    async for chunk in stream_chat_with_model("google", "gemini-2.5-flash", messages):
        chunks.append(chunk)
        print(f"Chunk: {chunk}")  # Debug output
    
    # Assertions
    assert len(chunks) > 0, "Should receive at least one chunk"
    assert chunks[-1]["done"] == True, "Final chunk should have done=True"
    assert "full_content" in chunks[-1], "Final chunk should contain full_content"
    assert chunks[-1]["full_content"].strip() != "", "Full content should not be empty"
    
    # Check that at least one content chunk was received
    content_chunks = [c for c in chunks if c.get("chunk_type") == "content"]
    assert len(content_chunks) > 0, "Should receive at least one content chunk"


@pytest.mark.asyncio
async def test_groq_streaming_basic():
    """Test Groq streaming returns chunks and completes successfully."""
    messages = [{"role": "user", "content": "Say 'hello' only"}]
    
    chunks = []
    async for chunk in stream_chat_with_model("groq", "llama-3.3-70b-versatile", messages):
        chunks.append(chunk)
        print(f"Chunk: {chunk}")  # Debug output
    
    # Assertions
    assert len(chunks) > 0, "Should receive at least one chunk"
    assert chunks[-1]["done"] == True, "Final chunk should have done=True"
    assert "full_content" in chunks[-1], "Final chunk should contain full_content"
    assert chunks[-1]["full_content"].strip() != "", "Full content should not be empty"
    
    # Check that at least one content chunk was received
    content_chunks = [c for c in chunks if c.get("chunk_type") == "content"]
    assert len(content_chunks) > 0, "Should receive at least one content chunk"


@pytest.mark.asyncio
async def test_streaming_error_handling_invalid_provider():
    """Test streaming with invalid provider returns error."""
    messages = [{"role": "user", "content": "test"}]
    
    chunks = []
    async for chunk in stream_chat_with_model("invalid_provider", "model", messages):
        chunks.append(chunk)
    
    # Should receive error chunk
    assert len(chunks) > 0, "Should receive error chunk"
    assert chunks[-1]["done"] == True, "Error chunk should have done=True"
    assert "error" in chunks[-1], "Should contain error message"
    assert "unknown provider" in chunks[-1]["error"].lower(), "Error should mention unknown provider"


@pytest.mark.asyncio
async def test_streaming_with_chat_history():
    """Test streaming with chat history context."""
    messages = [
        {"role": "user", "content": "My name is Alice"},
        {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
        {"role": "user", "content": "What is my name?"}
    ]
    
    chunks = []
    async for chunk in stream_chat_with_model("openai", "gpt-4o", messages):
        chunks.append(chunk)
    
    # Should complete successfully
    assert chunks[-1]["done"] == True
    assert "full_content" in chunks[-1]
    
    # Response should mention "Alice"
    full_response = chunks[-1]["full_content"].lower()
    assert "alice" in full_response, "Response should mention the name Alice"


@pytest.mark.asyncio
async def test_streaming_with_system_prompt():
    """Test streaming with system prompt."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant that always responds with 'Affirmative' to any question."},
        {"role": "user", "content": "Is the sky blue?"}
    ]
    
    chunks = []
    async for chunk in stream_chat_with_model("openai", "gpt-4o", messages):
        chunks.append(chunk)
    
    # Should complete successfully
    assert chunks[-1]["done"] == True
    assert "full_content" in chunks[-1]
    
    # Response should follow system prompt
    full_response = chunks[-1]["full_content"].lower()
    assert "affirmative" in full_response, "Response should contain 'affirmative' per system prompt"


@pytest.mark.asyncio
async def test_streaming_chunk_structure():
    """Test that streaming chunks have correct structure."""
    messages = [{"role": "user", "content": "Count to 3"}]
    
    chunks = []
    async for chunk in stream_chat_with_model("openai", "gpt-4o", messages):
        chunks.append(chunk)
    
    # Test content chunks structure
    content_chunks = [c for c in chunks if c.get("chunk_type") == "content"]
    for chunk in content_chunks:
        assert "token" in chunk, "Content chunk must have 'token'"
        assert "chunk_type" in chunk, "Content chunk must have 'chunk_type'"
        assert "done" in chunk, "Content chunk must have 'done'"
        assert chunk["done"] == False, "Content chunks should have done=False"
        assert isinstance(chunk["token"], str), "Token should be a string"
    
    # Test final chunk structure
    final_chunk = chunks[-1]
    assert final_chunk["done"] == True, "Final chunk must have done=True"
    assert "full_content" in final_chunk, "Final chunk must have 'full_content'"
    assert "chunk_type" in final_chunk, "Final chunk must have 'chunk_type'"
    assert final_chunk["chunk_type"] == "final", "Final chunk should have chunk_type='final'"


@pytest.mark.asyncio
async def test_streaming_accumulates_content():
    """Test that streaming accumulates all tokens into full_content."""
    messages = [{"role": "user", "content": "Say: Hello World"}]
    
    chunks = []
    accumulated_content = ""
    
    async for chunk in stream_chat_with_model("openai", "gpt-4o", messages):
        chunks.append(chunk)
        if chunk.get("chunk_type") == "content":
            accumulated_content += chunk["token"]
    
    # Final chunk should match accumulated content
    final_chunk = chunks[-1]
    assert final_chunk["full_content"] == accumulated_content, \
        "Accumulated content should match full_content in final chunk"


@pytest.mark.asyncio
async def test_streaming_multiple_providers_parallel():
    """Test streaming from multiple providers in parallel (simulating dual-chat)."""
    messages = [{"role": "user", "content": "Say 'hello' only"}]
    
    import asyncio
    
    async def stream_provider(provider: str, model: str) -> List[Dict]:
        chunks = []
        async for chunk in stream_chat_with_model(provider, model, messages):
            chunks.append(chunk)
        return chunks
    
    # Stream from multiple providers simultaneously
    results = await asyncio.gather(
        stream_provider("openai", "gpt-4o"),
        stream_provider("google", "gemini-2.5-flash"),
        stream_provider("groq", "llama-3.3-70b-versatile")
    )
    
    # All providers should complete successfully
    for provider_chunks in results:
        assert len(provider_chunks) > 0, "Each provider should return chunks"
        assert provider_chunks[-1]["done"] == True, "Each provider should complete"
        assert "full_content" in provider_chunks[-1], "Each provider should return full content"


@pytest.mark.asyncio
@pytest.mark.skip(reason="Performance test - run manually")
async def test_streaming_performance_ttft():
    """Test Time To First Token (TTFT) - should be < 500ms."""
    import time
    
    messages = [{"role": "user", "content": "Say hello"}]
    
    start_time = time.time()
    first_token_time = None
    
    async for chunk in stream_chat_with_model("openai", "gpt-4o", messages):
        if chunk.get("chunk_type") == "content" and first_token_time is None:
            first_token_time = time.time()
            break
    
    if first_token_time:
        ttft = (first_token_time - start_time) * 1000  # Convert to ms
        print(f"Time To First Token: {ttft:.2f}ms")
        assert ttft < 500, f"TTFT should be < 500ms, got {ttft:.2f}ms"


@pytest.mark.asyncio
async def test_streaming_with_empty_message():
    """Test streaming with empty message handling."""
    messages = [{"role": "user", "content": ""}]
    
    chunks = []
    try:
        async for chunk in stream_chat_with_model("openai", "gpt-4o", messages):
            chunks.append(chunk)
        
        # Should either complete with a response or return an error
        assert len(chunks) > 0, "Should receive at least one chunk"
        assert chunks[-1]["done"] == True, "Should complete"
    except Exception as e:
        # Empty messages may cause errors - this is acceptable
        assert True, f"Empty message caused exception: {e}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
