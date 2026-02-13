"""
Model Discovery Service
Dynamically fetches available models from LLM providers.
"""

from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Provider SDKs for model listing
import openai
import google.generativeai as genai
from groq import Groq

load_dotenv()


async def get_openai_models() -> List[Dict[str, Any]]:
    """
    Fetch flagship OpenAI chat models only.
    
    Returns only latest major versions, excluding dated variants, previews,
    and older generations (GPT-3.5).
    
    Returns:
        List of flagship model dicts
    """
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        models_response = client.models.list()
        
        print(f"[OpenAI] Total models from API: {len(models_response.data)}")
        
        # Exclude patterns for non-chat and non-flagship models
        exclude_patterns = [
            "whisper", "tts", "dall-e", "text-embedding", "text-moderation",
            "realtime", "audio", "image", "transcribe", "search",
            "babbage", "davinci", "curie", "ada",
            # Remove dated versions and older generations
            "-2024-", "-2025-", "-preview", "gpt-3.5", "gpt-4.1", "gpt-5.1", "gpt-5.2",
            "-instruct", "chatgpt-", "-latest", "-codex",
        ]
        
        # Flagship models to KEEP (using model ID patterns)
        flagship_patterns = [
            "gpt-5-mini", "gpt-5-nano", "gpt-5$",  # Latest GPT-5 series
            "gpt-4o-mini", "gpt-4o$", "gpt-4-turbo", "gpt-4$",  # GPT-4 series
            "o1-mini", "o1-pro", "o1$", "o3-mini", "o3$",  # Reasoning models
        ]
        
        chat_models = []
        filtered_out = []
        
        for model in models_response.data:
            model_id = model.id.lower()
            
            # Skip if matches any exclude pattern
            if any(pattern in model_id for pattern in exclude_patterns):
                filtered_out.append(f"{model.id} (excluded)")
                continue
            
            # Only include if matches flagship pattern
            import re
            is_flagship = any(
                re.search(pattern.replace("$", "$"), model_id) if "$" in pattern 
                else pattern in model_id
                for pattern in flagship_patterns
            )
            
            if is_flagship:
                chat_models.append({
                    "id": model.id,
                    "name": model.id,
                    "provider": "openai",
                    "created": model.created,
                    "owned_by": model.owned_by,
                })
            else:
                filtered_out.append(f"{model.id} (not flagship)")
        
        print(f"[OpenAI] Filtered out {len(filtered_out)} models")
        print(f"[OpenAI] Flagship models: {len(chat_models)}")
        if chat_models:
            print(f"[OpenAI] Models: {[m['id'] for m in chat_models]}")
        
        return sorted(chat_models, key=lambda x: x["created"], reverse=True)
    except Exception as e:
        print(f"Error fetching OpenAI models: {e}")
        return []


async def get_google_models() -> List[Dict[str, Any]]:
    """
    Fetch flagship Google Gemini chat models only.
    
    Returns only latest major versions (Gemini 3, 2.5, 2.0),
    excluding dated variants, experimental models, and specialized variants.
    
    Returns:
        List of flagship model dicts
    """
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        models = list(genai.list_models())
        
        print(f"[Google] Total models from API: {len(models)}")
        
        # Exclude patterns
        exclude_patterns = [
            "embedding", "aqa", "vision", "-tts", "-image", "image-",
            "robotics", "computer-use", "deep-research", "gemma",
            # Remove dated/versioned variants
            "-001", "-09-2025", "-10-2025", "-12-2025",
            "-exp-", "nano-banana", "-latest",
        ]
        
        # Flagship models to KEEP
        flagship_patterns = [
            "gemini-3-pro", "gemini-3-flash",  # Latest Gemini 3
            "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite",  # Gemini 2.5
            "gemini-2.0-flash-lite", "gemini-2.0-flash",  # Gemini 2.0
        ]
        
        chat_models = []
        filtered_out = []
        
        for model in models:
            clean_name = model.name.replace("models/", "")
            model_name_lower = clean_name.lower()
            
            # Skip if matches any exclude pattern
            if any(pattern in model_name_lower for pattern in exclude_patterns):
                filtered_out.append(f"{clean_name} (excluded)")
                continue
            
            # Must support generateContent
            if "generateContent" not in model.supported_generation_methods:
                filtered_out.append(f"{clean_name} (no generateContent)")
                continue
            
            # Only include flagship models
            is_flagship = any(pattern in model_name_lower for pattern in flagship_patterns)
            
            if is_flagship:
                chat_models.append({
                    "id": clean_name,
                    "name": clean_name,
                    "provider": "google",
                    "display_name": model.display_name,
                    "description": model.description,
                    "supported_methods": model.supported_generation_methods,
                })
            else:
                filtered_out.append(f"{clean_name} (not flagship)")
        
        print(f"[Google] Filtered out {len(filtered_out)} models")
        print(f"[Google] Flagship models: {len(chat_models)}")
        if chat_models:
            print(f"[Google] Models: {[m['id'] for m in chat_models]}")
        
        return chat_models
    except Exception as e:
        print(f"Error fetching Google models: {e}")
        return []


async def get_groq_models() -> List[Dict[str, Any]]:
    """
    Fetch flagship Groq LLaMA models only.
    
    Returns only main LLaMA 3.3 and 3.1 models, excluding guard/safety models,
    non-Meta models, and specialized variants.
    
    Returns:
        List of flagship model dicts
    """
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        models_response = client.models.list()
        
        print(f"[Groq] Total models from API: {len(models_response.data)}")
        
        # Exclude patterns
        exclude_patterns = [
            "whisper", "embedding", "guard", "safeguard", "orpheus",
            # Non-LLaMA models
            "kimi", "compound", "gpt-oss", "allam", "qwen", "openai/", "canopylabs/", "moonshotai/",
            # Specialized LLaMA variants
            "-scout", "-maverick", "llama-4",  # Experimental variants
        ]
        
        # Flagship LLaMA models to KEEP
        flagship_patterns = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
        ]
        
        chat_models = []
        filtered_out = []
        
        for model in models_response.data:
            model_id = model.id.lower()
            
            # Skip if matches any exclude pattern
            if any(pattern in model_id for pattern in exclude_patterns):
                filtered_out.append(f"{model.id} (excluded)")
                continue
            
            # Must be active
            if not model.active:
                filtered_out.append(f"{model.id} (inactive)")
                continue
            
            # Only include flagship models
            is_flagship = any(pattern in model_id for pattern in flagship_patterns)
            
            if is_flagship:
                chat_models.append({
                    "id": model.id,
                    "name": model.id,
                    "provider": "groq",
                    "created": model.created,
                    "owned_by": model.owned_by,
                    "active": model.active,
                })
            else:
                filtered_out.append(f"{model.id} (not flagship)")
        
        print(f"[Groq] Filtered out {len(filtered_out)} models")
        print(f"[Groq] Chat models found: {len(chat_models)}")
        if chat_models:
            print(f"[Groq] Models: {[m['id'] for m in chat_models]}")
        
        return sorted(chat_models, key=lambda x: x.get("created", 0), reverse=True)
    except Exception as e:
        print(f"Error fetching Groq models: {e}")
        return []


async def get_all_models() -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch available models from all providers.
    
    Returns:
        Dict with provider names as keys and model lists as values
    """
    return {
        "openai": await get_openai_models(),
        "google": await get_google_models(),
        "groq": await get_groq_models(),
    }


async def get_featured_models() -> Dict[str, List[Dict[str, str]]]:
    """
    Get curated list of featured/recommended models for each provider.
    
    This is useful for frontend UIs that want to show only the most relevant models.
    
    Returns:
        Dict with provider names and their featured models
    """
    # Hardcoded featured models (you can make this dynamic too)
    return {
        "openai": [
            {"id": "gpt-5", "name": "GPT-5", "description": "Most capable model"},
            {"id": "gpt-5-mini", "name": "GPT-5 Mini", "description": "Fast and affordable"},
            {"id": "gpt-nano", "name": "GPT Nano", "description": "Ultra-fast responses"},
        ],
        "google": [
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "description": "Most advanced reasoning"},
            {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "description": "Fast multimodal model"},
            {"id": "gemini-2.5-flash-lite", "name": "Gemini 2.5 Flash Lite", "description": "Lightweight model"},
        ],
        "groq": [
            {"id": "llama-3.3-70b-versatile", "name": "LLaMA 3.3 70B", "description": "High performance"},
            {"id": "llama-3.1-8b-instant", "name": "LLaMA 3.1 8B", "description": "Ultra-fast inference"},
        ],
    }


if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("Fetching all available models...\n")
        
        all_models = await get_all_models()
        
        print(f"OpenAI Models: {len(all_models['openai'])} found")
        for model in all_models['openai'][:5]:  # Show first 5
            print(f"  - {model['id']}")
        
        print(f"\nGoogle Gemini Models: {len(all_models['google'])} found")
        for model in all_models['google']:
            print(f"  - {model['id']} ({model['display_name']})")
        
        print(f"\nGroq Models: {len(all_models['groq'])} found")
        for model in all_models['groq']:
            print(f"  - {model['id']}")
        
        print("\n" + "="*50)
        print("Featured Models:")
        featured = await get_featured_models()
        for provider, models in featured.items():
            print(f"\n{provider.upper()}:")
            for model in models:
                print(f"  - {model['name']}: {model['description']}")
    
    asyncio.run(test())
