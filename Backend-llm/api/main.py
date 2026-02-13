# Backend-llm/api/main.py
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Body, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
import json

from api.schema.models import QueryResponse, SingleModelChatRequest, ModelProvider

# NEW: Unified LangChain service + Model Discovery
from api.services.langchain_service import chat_with_model, stream_chat_with_model
from api.services.model_discovery_service import get_all_models, get_featured_models


# Helper function to validate model names dynamically
async def validate_model_for_provider(model_name: str, provider: str) -> bool:
    """
    Validate that a model name exists for the given provider.
    Uses the model discovery service to check available models.
    """
    all_models = await get_all_models()
    provider_models = all_models.get(provider.lower(), [])
    return any(m["id"] == model_name for m in provider_models)

# DEPRECATED: Legacy provider services (kept for reference)
# from api.services.openai_service import chat_with_model as openai_chat_with_model
# from api.services.google_gemini_service import chat_with_model as google_chat_with_model
# from api.services.groq_service import chat_with_model as groq_chat_with_model

app = FastAPI(
    title="TellMeMore LLM Models API",
    description="API with separate endpoints for querying different LLM providers with chat history support.",
    version="0.1",
)

# --- CORS Configuration ---
origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080,https://frontend-ui-301474384730.us-east4.run.app").split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- OpenAI Endpoint ---


@app.post("/chat/openai/{model_name}", response_model=QueryResponse, tags=["OpenAI Chat"])
async def chat_with_openai_model(
    model_name: str = Path(
        ..., description="The OpenAI model to use for the chat. Supported: gpt-5, gpt-5-mini, gpt-nano"),
    request_body: SingleModelChatRequest = Body(...)
):
    # Validate model name exists for OpenAI
    if not await validate_model_for_provider(model_name, "openai"):
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_name}' is not a valid OpenAI model. Use /models/featured to see available models."
        )

    # Build messages array: system_prompts + chat_history + current question
    messages = request_body.chat_history or []

    # Prepend system prompts if provided
    if request_body.system_prompts:
        for prompt in request_body.system_prompts:
            messages.insert(0, {"role": "system", "content": prompt})

    messages.append({"role": "user", "content": request_body.question})

    request_time = datetime.now(timezone.utc)
    # Use unified LangChain service
    result = await chat_with_model(
        provider="openai",
        model_name=model_name,
        messages=messages,
        **(request_body.extra_params if hasattr(request_body, 'extra_params') else {})
    )
    response_time = datetime.now(timezone.utc)
    latency = (response_time - request_time).total_seconds() * 1000
    return QueryResponse(
        answer=result.get("answer"),
        raw_response=result.get("raw"),
        session_id=request_body.session_id,
        model=model_name,
        provider=ModelProvider.OPENAI,
        error_message=result.get("error"),
        request_timestamp=request_time,
        response_timestamp=response_time,
        latency_ms=latency,
        usage=result.get("usage")
    )


@app.post("/chat/openai/{model_name}/stream", tags=["OpenAI Chat Streaming"])
async def stream_chat_with_openai_model(
    model_name: str = Path(
        ..., description="The OpenAI model to use for streaming chat. Supported: gpt-5, gpt-5-mini, gpt-nano"),
    request_body: SingleModelChatRequest = Body(...)
):
    """
    Stream chat responses from OpenAI models token-by-token using Server-Sent Events (SSE).
    
    Returns:
        StreamingResponse with text/event-stream content
        
    SSE Event Format:
        data: {"token": "Hello", "chunk_type": "content", "done": false}
        
        data: {"token": "", "chunk_type": "final", "done": true, "full_content": "Hello world", "usage": {...}}
        
    Error Event:
        data: {"error": "Error message", "done": true}
    """
    if not await validate_model_for_provider(model_name, "openai"):
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_name}' is not a valid OpenAI model."
        )
    
    # Build messages array: system_prompts + chat_history + current question
    messages = request_body.chat_history or []
    
    # Prepend system prompts if provided
    if request_body.system_prompts:
        for prompt in request_body.system_prompts:
            messages.insert(0, {"role": "system", "content": prompt})
    
    messages.append({"role": "user", "content": request_body.question})
    
    # Create async generator for streaming
    async def generate_stream():
        try:
            async for chunk_data in stream_chat_with_model(
                provider="openai",
                model_name=model_name,
                messages=messages,
                **(request_body.extra_params if hasattr(request_body, 'extra_params') else {})
            ):
                # Format as SSE: "data: {json}\n\n"
                yield f"data: {json.dumps(chunk_data)}\n\n"
        except Exception as e:
            # Send error event
            error_data = {"error": str(e), "done": True}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@app.post("/chat/google/{model_name_path}/stream", tags=["Google Chat Streaming"])
async def stream_chat_with_google_model(
    model_name_path: str = Path(
        ..., description="The Google Gemini model to use for streaming chat. Supported: gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite"),
    request_body: SingleModelChatRequest = Body(...)
):
    """
    Stream chat responses from Google Gemini models token-by-token using Server-Sent Events (SSE).
    
    Returns:
        StreamingResponse with text/event-stream content
        
    SSE Event Format:
        data: {"token": "Hello", "chunk_type": "content", "done": false}
        
        data: {"token": "", "chunk_type": "final", "done": true, "full_content": "Hello world", "usage": {...}}
    """
    if not await validate_model_for_provider(model_name_path, "google"):
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_name_path}' is not a Google model."
        )
    
    # Build messages array: system_prompts + chat_history + current question
    messages = request_body.chat_history or []
    
    # Prepend system prompts if provided
    if request_body.system_prompts:
        for prompt in request_body.system_prompts:
            messages.insert(0, {"role": "system", "content": prompt})
    
    messages.append({"role": "user", "content": request_body.question})
    
    # Create async generator for streaming
    async def generate_stream():
        try:
            async for chunk_data in stream_chat_with_model(
                provider="google",
                model_name=model_name_path,
                messages=messages,
                **(request_body.extra_params if hasattr(request_body, 'extra_params') else {})
            ):
                # Format as SSE: "data: {json}\n\n"
                yield f"data: {json.dumps(chunk_data)}\n\n"
        except Exception as e:
            # Send error event
            error_data = {"error": str(e), "done": True}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@app.post("/chat/groq/{model_name_path}/stream", tags=["Groq Chat Streaming"])
async def stream_chat_with_groq_model(
    model_name_path: str = Path(
        ..., description="The Groq LLaMA model to use for streaming chat. Supported: llama-3.3-70b-versatile, llama-3.1-8b-instant"),
    request_body: SingleModelChatRequest = Body(...)
):
    """
    Stream chat responses from Groq LLaMA models token-by-token using Server-Sent Events (SSE).
    
    Returns:
        StreamingResponse with text/event-stream content
        
    SSE Event Format:
        data: {"token": "Hello", "chunk_type": "content", "done": false}
        
        data: {"token": "", "chunk_type": "final", "done": true, "full_content": "Hello world", "usage": {...}}
    """
    if not await validate_model_for_provider(model_name_path, "groq"):
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_name_path}' is not a Groq model."
        )
    
    # Build messages array: system_prompts + chat_history + current question
    messages = request_body.chat_history or []
    
    # Prepend system prompts if provided
    if request_body.system_prompts:
        for prompt in request_body.system_prompts:
            messages.insert(0, {"role": "system", "content": prompt})
    
    messages.append({"role": "user", "content": request_body.question})
    
    # Create async generator for streaming
    async def generate_stream():
        try:
            async for chunk_data in stream_chat_with_model(
                provider="groq",
                model_name=model_name_path,
                messages=messages,
                **(request_body.extra_params if hasattr(request_body, 'extra_params') else {})
            ):
                # Format as SSE: "data: {json}\n\n"
                yield f"data: {json.dumps(chunk_data)}\n\n"
        except Exception as e:
            # Send error event
            error_data = {"error": str(e), "done": True}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


# --- Google Endpoint ---


@app.post("/chat/google/{model_name_path}", response_model=QueryResponse, tags=["Google Chat"])
async def chat_with_google_model(
    model_name_path: str = Path(
        ..., description="The specific Google Gemini model name to use. Supported: gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite"),
    request_body: SingleModelChatRequest = Body(...)
):
    if not await validate_model_for_provider(model_name_path, "google"):
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_name_path}' is not a valid Google model. Use /models/featured to see available models."
        )

    # Build messages array: system_prompts + chat_history + current question
    messages = request_body.chat_history or []

    # Prepend system prompts if provided
    if request_body.system_prompts:
        for prompt in request_body.system_prompts:
            messages.insert(0, {"role": "system", "content": prompt})

    messages.append({"role": "user", "content": request_body.question})

    request_time = datetime.now(timezone.utc)
    # Use unified LangChain service
    result = await chat_with_model(
        provider="google",
        model_name=model_name_path,
        messages=messages,
        **(request_body.extra_params if hasattr(request_body, 'extra_params') else {})
    )
    response_time = datetime.now(timezone.utc)
    latency = (response_time - request_time).total_seconds() * 1000
    return QueryResponse(
        answer=result.get("answer"),
        raw_response=result.get("raw"),
        session_id=request_body.session_id,
        model=model_name_path,
        provider=ModelProvider.GOOGLE,
        error_message=result.get("error"),
        request_timestamp=request_time,
        response_timestamp=response_time,
        latency_ms=latency,
        usage=result.get("usage"),  # Include token usage
    )
# --- Groq Endpoint ---


@app.post("/chat/groq/{model_name_path}", response_model=QueryResponse, tags=["Groq Chat"])
async def chat_with_groq_model(
    model_name_path: str = Path(
        ..., description="The specific Groq LLaMA3 model name to use. Supported: llama-3.3-70b-versatile, llama-3.1-8b-instant"),
    request_body: SingleModelChatRequest = Body(...)
):
    if not await validate_model_for_provider(model_name_path, "groq"):
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_name_path}' is not a valid Groq model. Use /models/featured to see available models."
        )

    # Build messages array: system_prompts + chat_history + current question
    messages = request_body.chat_history or []

    # Prepend system prompts if provided
    if request_body.system_prompts:
        for prompt in request_body.system_prompts:
            messages.insert(0, {"role": "system", "content": prompt})

    messages.append({"role": "user", "content": request_body.question})

    request_time = datetime.now(timezone.utc)
    # Use unified LangChain service
    result = await chat_with_model(
        provider="groq",
        model_name=model_name_path,
        messages=messages,
        **(request_body.extra_params if hasattr(request_body, 'extra_params') else {})
    )
    response_time = datetime.now(timezone.utc)
    latency = (response_time - request_time).total_seconds() * 1000
    return QueryResponse(
        answer=result.get("answer"),
        raw_response=result.get("raw"),
        session_id=request_body.session_id,
        model=model_name_path,
        provider=ModelProvider.GROQ,
        error_message=result.get("error"),
        request_timestamp=request_time,
        response_timestamp=response_time,
        latency_ms=latency,
        usage=result.get("usage"),  # Include token usage
    )


# --- Model Discovery Endpoints ---

@app.get("/models", tags=["Model Discovery"])
async def list_all_models():
    """Get all available models from OpenAI, Google Gemini, and Groq."""
    try:
        models = await get_all_models()
        return {
            "success": True,
            "models": models,
            "total_count": {
                "openai": len(models["openai"]),
                "google": len(models["google"]),
                "groq": len(models["groq"]),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")


@app.get("/models/featured", tags=["Model Discovery"])
async def list_featured_models():
    """Get curated list of featured/recommended models."""
    try:
        featured = await get_featured_models()
        return {"success": True, "featured_models": featured}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch featured models: {str(e)}")


@app.get("/models/{provider}", tags=["Model Discovery"])
async def list_provider_models(provider: str):
    """Get available models for a specific provider (openai/google/groq)."""
    provider = provider.lower()
    if provider not in ["openai", "google", "groq"]:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
    try:
        all_models = await get_all_models()
        return {
            "success": True,
            "provider": provider,
            "models": all_models.get(provider, []),
            "count": len(all_models.get(provider, [])),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch {provider} models: {str(e)}")
