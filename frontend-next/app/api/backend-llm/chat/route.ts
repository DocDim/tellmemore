/**
 * BFF API Route: LLM Chat
 * 
 * Proxies chat requests to Backend-llm for various LLM providers.
 * Handles authentication, request validation, and quota updates.
 * 
 * Endpoints:
 * - POST /api/backend-llm/chat - Send chat message to LLM
 * 
 * Supports:
 * - OpenAI (GPT-5, GPT-5 Mini, GPT Nano)
 * - Google Gemini (2.5 Pro, 2.5 Flash, 2.5 Flash Lite)
 * - Groq (LLaMA 3.3 70B, LLaMA 3.1 8B)
 */

import { auth } from '@clerk/nextjs/server';
import { NextRequest, NextResponse } from 'next/server';
import { env } from '@/lib/env';

/**
 * TypeScript types matching Backend-llm schemas
 */
interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface ChatRequest {
  question: string;
  session_id?: string;
  chat_history?: ChatMessage[];
  model: string;
  provider: 'openai' | 'google' | 'groq';
}

interface ChatResponse {
  answer: string | null;
  raw_response?: unknown;
  error_message?: string | null;
  session_id: string;
  model: string;
  provider: string;
  request_timestamp: string;
  response_timestamp: string;
  latency_ms: number;
  usage?: Record<string, unknown>; // Token usage info (varies by provider)
}

interface ErrorResponse {
  error: string;
  detail?: string;
}

/**
 * POST /api/backend-llm/chat
 * 
 * Send a chat message to the specified LLM model.
 * 
 * Authentication: Required (Clerk JWT)
 * 
 * Request Body:
 * - question: string (required) - The user's message/prompt
 * - model: string (required) - Model name (e.g., "gpt-5", "gemini-2.5-flash", "llama-3.3-70b-versatile")
 * - session_id: string (optional) - Chat session ID
 * - chat_history: ChatMessage[] (optional) - Previous conversation history
 * 
 * Response:
 * - 200: ChatResponse (LLM's response with metadata)
 * - 400: Bad request (invalid model, missing question, etc.)
 * - 401: Unauthorized (no valid Clerk session)
 * - 429: Too many requests (quota exceeded)
 * - 500: Internal server error
 * - 502: Bad gateway (LLM service error)
 */
export async function POST(request: NextRequest): Promise<NextResponse<ChatResponse | ErrorResponse>> {
  try {
    // Authenticate user via Clerk
    const { userId } = await auth();
    
    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized', detail: 'No valid Clerk session found' },
        { status: 401 }
      );
    }

    // Parse request body
    const body = await request.json().catch(() => null);
    
    if (!body) {
      return NextResponse.json(
        { error: 'Bad request', detail: 'Invalid JSON body' },
        { status: 400 }
      );
    }

    // Validate required fields
    const { question, model, provider, session_id, chat_history } = body as ChatRequest;

    if (!question || typeof question !== 'string' || question.trim().length === 0) {
      return NextResponse.json(
        { error: 'Bad request', detail: 'Missing or empty "question" field' },
        { status: 400 }
      );
    }

    if (!model || typeof model !== 'string') {
      return NextResponse.json(
        { error: 'Bad request', detail: 'Missing or invalid "model" field' },
        { status: 400 }
      );
    }

    if (!provider || typeof provider !== 'string') {
      return NextResponse.json(
        { error: 'Bad request', detail: 'Missing or invalid "provider" field' },
        { status: 400 }
      );
    }

    // Validate chat_history if provided
    if (chat_history && !Array.isArray(chat_history)) {
      return NextResponse.json(
        { error: 'Bad request', detail: '"chat_history" must be an array' },
        { status: 400 }
      );
    }

    // Prepare request payload for Backend-llm
    const llmPayload = {
      question: question.trim(),
      session_id: session_id || undefined,
      chat_history: chat_history || [],
    };

    // Send request to Backend-llm
    const llmResponse = await fetch(
      `${env.server.backendLlmUrl}/chat/${provider}/${model}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(llmPayload),
      }
    );

    if (!llmResponse.ok) {
      const errorData = await llmResponse.json().catch(() => ({ detail: 'Unknown error' }));
      console.error('Backend-llm error:', errorData);
      
      // LLM service error (rate limit, API error, etc.)
      return NextResponse.json(
        { 
          error: 'LLM service error', 
          detail: errorData.detail || errorData.error_message || 'Failed to get response from LLM' 
        },
        { status: 502 }
      );
    }

    const chatResponse: ChatResponse = await llmResponse.json();

    // DEBUG: Log usage data
    // console.log('🔍 Backend-llm response usage:', {
    //   model,
    //   provider,
    //   usage: chatResponse.usage,
    //   hasUsage: !!chatResponse.usage,
    // });

    return NextResponse.json(chatResponse, { status: 200 });
  } catch (error) {
    console.error('BFF error in POST /api/backend-llm/chat:', error);
    
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        detail: error instanceof Error ? error.message : 'Unknown error' 
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/backend-llm/chat?stream=true&model=gpt-5&question=Hello&session_id=123
 * 
 * Stream chat responses from LLM using Server-Sent Events (SSE).
 * 
 * Authentication: Required (Clerk JWT)
 * 
 * Query Parameters:
 * - question: string (required) - The user's message/prompt
 * - model: string (required) - Model name (e.g., "gpt-5", "gemini-2.5-flash")
 * - stream: boolean (required) - Must be "true" for streaming
 * - session_id: string (optional) - Chat session ID
 * 
 * Response:
 * - 200: text/event-stream (SSE)
 *   - Content chunks: data: {"token": "Hello", "chunk_type": "content", "done": false}\n\n
 *   - Final chunk: data: {"token": "", "chunk_type": "final", "done": true, "full_content": "...", "usage": {...}}\n\n
 * - 400: Bad request (invalid parameters)
 * - 401: Unauthorized (no valid Clerk session)
 * - 502: Bad gateway (LLM service error)
 */
export async function GET(request: NextRequest): Promise<Response> {
  try {
    // Authenticate user via Clerk
    const { userId } = await auth();
    
    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized', detail: 'No valid Clerk session found' },
        { status: 401 }
      );
    }

    // Parse query parameters
    const searchParams = request.nextUrl.searchParams;
    const question = searchParams.get('question');
    const model = searchParams.get('model');
    const provider = searchParams.get('provider');
    const stream = searchParams.get('stream');
    const session_id = searchParams.get('session_id');

    // Validate required parameters
    if (!question || question.trim().length === 0) {
      return NextResponse.json(
        { error: 'Bad request', detail: 'Missing or empty "question" parameter' },
        { status: 400 }
      );
    }

    if (!model) {
      return NextResponse.json(
        { error: 'Bad request', detail: 'Missing "model" parameter' },
        { status: 400 }
      );
    }

    if (!provider) {
      return NextResponse.json(
        { error: 'Bad request', detail: 'Missing "provider" parameter' },
        { status: 400 }
      );
    }

    if (stream !== 'true') {
      return NextResponse.json(
        { error: 'Bad request', detail: 'Missing or invalid "stream" parameter (must be "true")' },
        { status: 400 }
      );
    }

    // Prepare query params for Backend-llm
    const backendParams = new URLSearchParams({
      question: question.trim(),
      session_id: session_id || '',
    });

    // Call Backend-llm streaming endpoint
    const backendUrl = `${env.server.backendLlmUrl}/chat/${provider}/${model}/stream?${backendParams.toString()}`;
    
    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: question.trim(),
        session_id: session_id || undefined,
        chat_history: [], // TODO: Support chat history in streaming
      }),
    });

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json().catch(() => ({ detail: 'Unknown error' }));
      console.error('Backend-llm streaming error:', errorData);
      
      return NextResponse.json(
        { 
          error: 'LLM service error', 
          detail: errorData.detail || errorData.error_message || 'Failed to start streaming from LLM' 
        },
        { status: 502 }
      );
    }

    // Proxy the SSE stream from Backend-llm to the client
    // This passes through the ReadableStream without buffering
    return new Response(backendResponse.body, {
      status: 200,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-transform',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
      },
    });
  } catch (error) {
    console.error('BFF error in GET /api/backend-llm/chat (streaming):', error);
    
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        detail: error instanceof Error ? error.message : 'Unknown error' 
      },
      { status: 500 }
    );
  }
}
