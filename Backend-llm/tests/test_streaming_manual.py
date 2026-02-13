#!/usr/bin/env python3
"""
Manual Streaming Test Script
Quick verification that streaming endpoints work correctly.

Usage:
    python test_streaming_manual.py [provider] [model]
    
Examples:
    python test_streaming_manual.py openai gpt-4o
    python test_streaming_manual.py google gemini-2.5-flash
    python test_streaming_manual.py groq llama-3.3-70b-versatile
"""

import asyncio
import httpx
import sys
import json
from datetime import datetime


async def test_streaming(provider: str, model: str, question: str = "Count to 5 slowly"):
    """Test streaming endpoint and display results in real-time."""
    
    base_url = "http://localhost:8001"  # Backend-llm default port
    url = f"{base_url}/chat/{provider}/{model}/stream"
    
    payload = {
        "question": question,
        "session_id": f"manual-test-{datetime.now().timestamp()}"
    }
    
    print(f"\n{'='*60}")
    print(f"Testing: {provider.upper()} / {model}")
    print(f"Question: {question}")
    print(f"URL: {url}")
    print(f"{'='*60}\n")
    
    start_time = datetime.now()
    first_token_time = None
    chunk_count = 0
    full_content = ""
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                print(f"Status: {response.status_code}")
                print(f"Headers: {dict(response.headers)}\n")
                
                if response.status_code != 200:
                    print(f"❌ Error: {response.status_code}")
                    print(await response.aread())
                    return
                
                print("Streaming response:")
                print("-" * 60)
                
                buffer = ""
                async for chunk in response.aiter_text():
                    buffer += chunk
                    
                    # Process complete lines (SSE format)
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])  # Remove 'data: ' prefix
                                
                                if data.get("error"):
                                    print(f"\n❌ Error: {data['error']}")
                                    return
                                
                                if data.get("chunk_type") == "content":
                                    token = data.get("token", "")
                                    if token:
                                        if first_token_time is None:
                                            first_token_time = datetime.now()
                                        print(token, end="", flush=True)
                                        full_content += token
                                        chunk_count += 1
                                
                                elif data.get("done"):
                                    end_time = datetime.now()
                                    print("\n" + "-" * 60)
                                    
                                    # Display metrics
                                    total_time = (end_time - start_time).total_seconds() * 1000
                                    ttft = (first_token_time - start_time).total_seconds() * 1000 if first_token_time else 0
                                    
                                    print(f"\n✅ Streaming complete!")
                                    print(f"\n📊 Metrics:")
                                    print(f"  - Chunks received: {chunk_count}")
                                    print(f"  - Content length: {len(full_content)} characters")
                                    print(f"  - Time to first token: {ttft:.2f}ms")
                                    print(f"  - Total time: {total_time:.2f}ms")
                                    
                                    if data.get("usage"):
                                        print(f"  - Token usage: {data['usage']}")
                                    
                                    # Verify full_content matches accumulated
                                    returned_full = data.get("full_content", "")
                                    if returned_full == full_content:
                                        print(f"  - ✓ Content integrity verified")
                                    else:
                                        print(f"  - ⚠️  Content mismatch!")
                                        print(f"    Expected length: {len(full_content)}")
                                        print(f"    Returned length: {len(returned_full)}")
                            
                            except json.JSONDecodeError as e:
                                print(f"\n❌ JSON decode error: {e}")
                                print(f"Line: {line}")
    
    except Exception as e:
        print(f"\n❌ Exception: {type(e).__name__}: {e}")


async def test_all_providers():
    """Test all providers with default models."""
    providers = [
        ("openai", "gpt-4o"),
        ("google", "gemini-2.5-flash"),
        ("groq", "llama-3.3-70b-versatile")
    ]
    
    for provider, model in providers:
        await test_streaming(provider, model, "Say 'hello' only")
        await asyncio.sleep(1)  # Brief pause between tests


async def compare_streaming_vs_non_streaming(provider: str, model: str):
    """Compare streaming vs non-streaming response times."""
    question = "What is the capital of France? Be concise."
    base_url = "http://localhost:8001"
    
    print(f"\n{'='*60}")
    print(f"Comparing Streaming vs Non-Streaming")
    print(f"Provider: {provider}, Model: {model}")
    print(f"{'='*60}\n")
    
    # Test non-streaming
    print("1️⃣  Non-Streaming Request...")
    start_ns = datetime.now()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{base_url}/chat/{provider}/{model}",
            json={"question": question, "session_id": "benchmark-ns"}
        )
    
    end_ns = datetime.now()
    time_ns = (end_ns - start_ns).total_seconds() * 1000
    
    if response.status_code == 200:
        data = response.json()
        answer_ns = data.get("answer", "")
        print(f"   ✓ Response: {answer_ns[:100]}...")
        print(f"   ✓ Time: {time_ns:.2f}ms")
    else:
        print(f"   ✗ Error: {response.status_code}")
    
    # Test streaming
    print("\n2️⃣  Streaming Request...")
    start_s = datetime.now()
    first_token_time = None
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", f"{base_url}/chat/{provider}/{model}/stream", json={"question": question, "session_id": "benchmark-s"}) as response:
            buffer = ""
            async for chunk in response.aiter_text():
                buffer += chunk
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    
                    if line.startswith('data: '):
                        data = json.loads(line[6:])
                        
                        if data.get("chunk_type") == "content" and first_token_time is None:
                            first_token_time = datetime.now()
                        
                        if data.get("done"):
                            end_s = datetime.now()
                            break
    
    time_s_total = (end_s - start_s).total_seconds() * 1000
    time_s_ttft = (first_token_time - start_s).total_seconds() * 1000 if first_token_time else 0
    
    print(f"   ✓ Time to first token: {time_s_ttft:.2f}ms")
    print(f"   ✓ Total time: {time_s_total:.2f}ms")
    
    # Comparison
    print(f"\n📊 Comparison:")
    print(f"   Non-Streaming total: {time_ns:.2f}ms")
    print(f"   Streaming TTFT: {time_s_ttft:.2f}ms (⚡ {(time_ns - time_s_ttft):.2f}ms faster perceived)")
    print(f"   Streaming total: {time_s_total:.2f}ms")
    
    if time_s_ttft < 500:
        print(f"   ✅ TTFT < 500ms target achieved!")
    else:
        print(f"   ⚠️  TTFT > 500ms (target not met)")


def print_usage():
    """Print usage instructions."""
    print(__doc__)
    print("\nAvailable Commands:")
    print("  test <provider> <model>  - Test specific provider/model")
    print("  test-all                 - Test all providers")
    print("  compare <provider> <model> - Compare streaming vs non-streaming")
    print("\nExamples:")
    print("  python test_streaming_manual.py test openai gpt-4o")
    print("  python test_streaming_manual.py test-all")
    print("  python test_streaming_manual.py compare openai gpt-4o")


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1]
    
    if command == "test" and len(sys.argv) >= 4:
        provider = sys.argv[2]
        model = sys.argv[3]
        question = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else "Count to 5 slowly"
        await test_streaming(provider, model, question)
    
    elif command == "test-all":
        await test_all_providers()
    
    elif command == "compare" and len(sys.argv) >= 4:
        provider = sys.argv[2]
        model = sys.argv[3]
        await compare_streaming_vs_non_streaming(provider, model)
    
    else:
        print_usage()


if __name__ == "__main__":
    asyncio.run(main())
