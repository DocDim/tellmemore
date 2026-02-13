"""
Unified LangChain Service
Provides a single interface for all LLM providers with automatic LangSmith tracing.
Supports both standard (ainvoke) and streaming (astream) chat operations.
"""

from typing import List, Dict, Any, Optional, Union, AsyncIterator
import os
import logging
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from pydantic import BaseModel

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _convert_messages_to_langchain(messages: List[Union[Dict[str, str], BaseMessage, Any]]) -> List[BaseMessage]:
    """
    Convert OpenAI-style message dicts or Pydantic models to LangChain message objects.
    
    Handles both:
    - Plain dicts with 'role' and 'content' keys
    - Pydantic BaseModel objects with role and content attributes
    
    Args:
        messages: List of message dicts or Pydantic models
        
    Returns:
        List of LangChain message objects
    """
    lc_messages = []
    for msg in messages:
        # Handle Pydantic models (ChatMessageAPI from FastAPI)
        if isinstance(msg, BaseModel):
            role = msg.role.lower() if hasattr(msg, 'role') else "user"
            content = msg.content if hasattr(msg, 'content') else ""
        # Handle plain dicts
        elif isinstance(msg, dict):
            role = msg.get("role", "user").lower()
            content = msg.get("content", "")
        else:
            # Fallback for unknown types
            role = "user"
            content = str(msg)
        
        if role == "system":
            lc_messages.append(SystemMessage(content=content))
        elif role == "user" or role == "human":
            lc_messages.append(HumanMessage(content=content))
        elif role == "assistant" or role == "ai":
            lc_messages.append(AIMessage(content=content))
        else:
            # Default to HumanMessage for unknown roles
            lc_messages.append(HumanMessage(content=content))
    
    return lc_messages


async def chat_with_model(
    provider: str,
    model_name: str,
    messages: List[Union[Dict[str, str], BaseModel, Any]],
    **kwargs
) -> Dict[str, Any]:
    """
    Unified chat interface for all providers using LangChain.
    
    Automatically traces all calls to LangSmith when LANGSMITH_TRACING=true.
    
    Args:
        provider: Provider name ('openai', 'google', 'groq')
        model_name: Model identifier (e.g., 'gpt-4o', 'gemini-2.5-flash')
        messages: List of message dicts or Pydantic models in OpenAI format
        **kwargs: Additional model parameters (temperature, max_tokens, etc.)
        
    Returns:
        Standardized response dict with answer, usage, and error info
    """
    try:
        # Initialize the appropriate chat model based on provider
        if provider.lower() == "openai":
            model = ChatOpenAI(
                model=model_name,
                api_key=os.getenv("OPENAI_API_KEY"),
                **kwargs
            )
        elif provider.lower() == "google":
            model = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                **kwargs
            )
        elif provider.lower() == "groq":
            model = ChatGroq(
                model=model_name,
                api_key=os.getenv("GROQ_API_KEY"),
                **kwargs
            )
        else:
            return {
                "answer": None,
                "raw": None,
                "usage": None,
                "error": f"Unknown provider: {provider}"
            }
        
        # Convert messages to LangChain format
        lc_messages = _convert_messages_to_langchain(messages)
        
        # Invoke model - automatically traced by LangSmith!
        response = await model.ainvoke(lc_messages)
        
        # Extract usage information (varies by provider)
        usage_dict = None
        if hasattr(response, 'response_metadata'):
            metadata = response.response_metadata
            
            # OpenAI format
            if 'token_usage' in metadata:
                usage_dict = metadata['token_usage']
            # Google Gemini format
            elif 'usage_metadata' in metadata:
                usage_dict = metadata['usage_metadata']
            # Groq format (similar to OpenAI)
            elif 'usage' in metadata:
                usage_dict = metadata['usage']
        
        # Return standardized response
        return {
            "answer": response.content,
            "raw": response.model_dump() if hasattr(response, 'model_dump') else str(response),
            "usage": usage_dict,
            "error": None
        }
        
    except Exception as e:
        return {
            "answer": None,
            "raw": None,
            "usage": None,
            "error": str(e)
        }


async def stream_chat_with_model(
    provider: str,
    model_name: str,
    messages: List[Union[Dict[str, str], BaseModel, Any]],
    **kwargs
) -> AsyncIterator[Dict[str, Any]]:
    """
    Unified streaming chat interface for all providers using LangChain.
    
    Streams LLM responses token-by-token using the astream() method.
    Automatically traces all calls to LangSmith when LANGSMITH_TRACING=true.
    
    Args:
        provider: Provider name ('openai', 'google', 'groq')
        model_name: Model identifier (e.g., 'gpt-4o', 'gemini-2.5-flash')
        messages: List of message dicts or Pydantic models in OpenAI format
        **kwargs: Additional model parameters (temperature, max_tokens, etc.)
        
    Yields:
        Dict[str, Any]: Chunk data with the following structure:
            - token: str - The content chunk from the LLM
            - chunk_type: str - Type of chunk ('content' or 'final')
            - done: bool - Whether streaming is complete
            - full_content: str (only in final chunk) - Complete response
            - usage: dict (only in final chunk, may be None) - Token usage info
            - error: str (only on error) - Error message if streaming failed
            
    Example:
        async for chunk in stream_chat_with_model("openai", "gpt-4o", messages):
            if chunk.get("error"):
                print(f"Error: {chunk['error']}")
            elif chunk.get("done"):
                print(f"Complete: {chunk['full_content']}")
            else:
                print(chunk["token"], end="", flush=True)
    """
    try:
        import time
        start_time = time.time()
        logger.info(f"Starting stream for {provider}/{model_name}")
        
        # Initialize the appropriate chat model based on provider
        if provider.lower() == "openai":
            # Enable stream_options to get usage data in streaming mode
            model_kwargs = {
                "stream_options": {"include_usage": True},
                **kwargs
            }
            model = ChatOpenAI(
                model=model_name,
                api_key=os.getenv("OPENAI_API_KEY"),
                **model_kwargs
            )
        elif provider.lower() == "google":
            model = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                **kwargs
            )
        elif provider.lower() == "groq":
            model = ChatGroq(
                model=model_name,
                api_key=os.getenv("GROQ_API_KEY"),
                **kwargs
            )
        else:
            logger.error(f"Unknown provider: {provider}")
            yield {
                "error": f"Unknown provider: {provider}",
                "done": True
            }
            return
        
        # Convert messages to LangChain format
        lc_messages = _convert_messages_to_langchain(messages)
        
        # Stream chunks using astream() - automatically traced by LangSmith!
        # TRUE token-by-token streaming (industry standard)
        full_content = ""
        chunk_count = 0
        first_token_time = None
        
        async for chunk in model.astream(lc_messages):
            # Extract content from AIMessageChunk
            chunk_content = chunk.content if hasattr(chunk, 'content') else str(chunk)
            
            if chunk_content:
                # Track time to first token
                if first_token_time is None:
                    first_token_time = time.time()
                    ttft = (first_token_time - start_time) * 1000  # Convert to ms
                    logger.info(f"Time to first token: {ttft:.2f}ms")
                
                full_content += chunk_content
                chunk_count += 1
                
                # Yield every single token immediately (industry standard streaming)
                logger.debug(f"Yielding token #{chunk_count}: {chunk_content[:50]}...")
                yield {
                    "token": chunk_content,
                    "chunk_type": "content",
                    "done": False
                }
        
        # Extract usage metadata from the last chunk if available
        # Note: OpenAI now includes usage via stream_options, others may vary
        usage_dict = None
        if hasattr(chunk, 'response_metadata'):
            metadata = chunk.response_metadata
            
            # OpenAI format (from stream_options)
            if 'token_usage' in metadata:
                usage_dict = metadata['token_usage']
            # Google Gemini format
            elif 'usage_metadata' in metadata:
                usage_dict = metadata['usage_metadata']
            # Groq format (similar to OpenAI)
            elif 'usage' in metadata:
                usage_dict = metadata['usage']
        
        # Also check usage_metadata attribute (OpenAI streaming with stream_options)
        if hasattr(chunk, 'usage_metadata') and chunk.usage_metadata:
            usage_dict = chunk.usage_metadata
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # Convert to ms
        logger.info(f"Stream complete: {len(full_content)} characters, {chunk_count} raw chunks, {total_time:.2f}ms total")
        
        # Final chunk with complete content and metadata
        yield {
            "token": "",
            "chunk_type": "final",
            "done": True,
            "full_content": full_content,
            "usage": usage_dict
        }
        
    except Exception as e:
        logger.error(f"Stream error for {provider}/{model_name}: {str(e)}")
        yield {
            "error": str(e),
            "done": True
        }


# For backward compatibility, provide provider-specific functions
async def chat_with_openai(model_name: str, messages: List[Union[Dict[str, str], BaseModel, Any]], **kwargs):
    """OpenAI-specific wrapper for backward compatibility."""
    return await chat_with_model("openai", model_name, messages, **kwargs)


async def chat_with_google(model_name: str, messages: List[Union[Dict[str, str], BaseModel, Any]], **kwargs):
    """Google Gemini-specific wrapper for backward compatibility."""
    return await chat_with_model("google", model_name, messages, **kwargs)


async def chat_with_groq(model_name: str, messages: List[Union[Dict[str, str], BaseModel, Any]], **kwargs):
    """Groq-specific wrapper for backward compatibility."""
    return await chat_with_model("groq", model_name, messages, **kwargs)


if __name__ == "__main__":
    import asyncio
    
    # Test OpenAI
    async def test_openai():
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]
        result = await chat_with_model("openai", "gpt-4o", messages)
        print("OpenAI Test Result:")
        print(f"Answer: {result['answer']}")
        print(f"Usage: {result['usage']}")
        print(f"Error: {result['error']}")
    
    # Test Google Gemini
    async def test_google():
        messages = [
            {"role": "user", "content": "What is the capital of France?"}
        ]
        result = await chat_with_model("google", "gemini-2.5-flash", messages)
        print("\nGoogle Gemini Test Result:")
        print(f"Answer: {result['answer']}")
        print(f"Usage: {result['usage']}")
        print(f"Error: {result['error']}")
    
    # Test Groq
    async def test_groq():
        messages = [
            {"role": "user", "content": "What is the capital of France?"}
        ]
        result = await chat_with_model("groq", "llama-3.3-70b-versatile", messages)
        print("\nGroq LLaMA Test Result:")
        print(f"Answer: {result['answer']}")
        print(f"Usage: {result['usage']}")
        print(f"Error: {result['error']}")
    
    # Run tests
    asyncio.run(test_openai())
    asyncio.run(test_google())
    asyncio.run(test_groq())
