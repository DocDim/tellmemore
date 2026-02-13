/**
 * Type-safe API client for all BFF endpoints
 * 
 * This client provides methods for all backend operations.
 * All requests go through the BFF layer (Next.js API routes).
 * 
 * Usage:
 * ```ts
 * import { apiClient } from '@/lib/api/client';
 * 
 * const sessions = await apiClient.sessions.list();
 * const newSession = await apiClient.sessions.create({ title: 'My Chat' });
 * ```
 */

import type {
  ChatSession,
  CreateSessionRequest,
  Prompt,
  CreatePromptRequest,
  ChatRequest,
  ChatResponse,
  Quota,
  UserPrompt,
  CreateUserPromptRequest,
  SystemPrompt,
  AuthStatus,
  ApiError,
  AllModelsResponse,
  FeaturedModelsResponse,
} from './types';

/**
 * Base fetch wrapper with error handling
 */
async function fetchApi<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({
      error: 'Request failed',
      detail: `HTTP ${response.status}: ${response.statusText}`,
    }));
    throw new Error(error.detail || error.error);
  }

  return response.json();
}

/**
 * Chat Sessions API
 */
export const sessionsApi = {
  /**
   * Get all sessions for the current user
   */
  list: async (): Promise<ChatSession[]> => {
    return fetchApi<ChatSession[]>('/api/backend-da/sessions');
  },

  /**
   * Create a new chat session
   */
  create: async (data: CreateSessionRequest): Promise<ChatSession> => {
    return fetchApi<ChatSession>('/api/backend-da/sessions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get a specific session by ID (future)
   */
  get: async (sessionId: string): Promise<ChatSession> => {
    return fetchApi<ChatSession>(`/api/backend-da/sessions/${sessionId}`);
  },

  /**
   * Update a session (future)
   */
  update: async (sessionId: string, data: Partial<CreateSessionRequest>): Promise<ChatSession> => {
    return fetchApi<ChatSession>(`/api/backend-da/sessions/${sessionId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete a session (future)
   */
  delete: async (sessionId: string): Promise<{ message: string }> => {
    return fetchApi<{ message: string }>(`/api/backend-da/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  },
};

/**
 * Prompts (Chat History) API
 */
export const promptsApi = {
  /**
   * Get all prompts for a session (chat history)
   */
  list: async (sessionId: string): Promise<Prompt[]> => {
    return fetchApi<Prompt[]>(`/api/backend-da/prompts?session_id=${sessionId}`);
  },

  /**
   * Save a new prompt and LLM responses
   */
  create: async (data: CreatePromptRequest): Promise<Prompt> => {
    return fetchApi<Prompt>('/api/backend-da/prompts', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

/**
 * LLM Chat API
 */
export const chatApi = {
  /**
   * Send a chat message to an LLM (non-streaming)
   */
  send: async (data: ChatRequest): Promise<ChatResponse> => {
    return fetchApi<ChatResponse>('/api/backend-llm/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Send a chat message to an LLM with streaming (SSE)
   * 
   * Returns an async generator that yields StreamChunk objects.
   * 
   * Usage:
   * ```ts
   * const stream = chatApi.sendStream({ question: 'Hello', model: 'gpt-5' });
   * for await (const chunk of stream) {
   *   console.log(chunk.token); // Display token
   *   if (chunk.done) {
   *     console.log('Stream complete:', chunk.full_content);
   *   }
   * }
   * ```
   */
  sendStream: async function* (data: ChatRequest): AsyncGenerator<import('./types').StreamChunk> {
    // Build query params
    const params = new URLSearchParams({
      question: data.question,
      model: data.model,
      provider: data.provider,
      stream: 'true',
      ...(data.session_id && { session_id: data.session_id }),
    });

    const response = await fetch(`/api/backend-llm/chat?${params.toString()}`, {
      method: 'GET',
      headers: {
        'Accept': 'text/event-stream',
      },
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        error: 'Streaming failed',
        detail: `HTTP ${response.status}: ${response.statusText}`,
      }));
      throw new Error(error.detail || error.error);
    }

    if (!response.body) {
      throw new Error('No response body for streaming');
    }

    // Parse SSE stream
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Split by SSE message delimiter (\n\n)
        const lines = buffer.split('\n\n');
        
        // Keep incomplete message in buffer
        buffer = lines.pop() || '';

        // Process complete messages
        for (const line of lines) {
          if (!line.trim()) continue;
          
          // SSE format: "data: {json}\n"
          if (line.startsWith('data: ')) {
            const jsonStr = line.slice(6); // Remove "data: " prefix
            try {
              const chunk = JSON.parse(jsonStr) as import('./types').StreamChunk;
              yield chunk;
              
              // Stop if done
              if (chunk.done) {
                return;
              }
            } catch (e) {
              console.error('Failed to parse SSE chunk:', jsonStr, e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },
};

/**
 * User Quota API
 */
export const quotaApi = {
  /**
   * Get current user's quota
   */
  get: async (): Promise<Quota> => {
    return fetchApi<Quota>('/api/backend-da/quota');
  },
};

/**
 * User Prompts (Custom Prompt Library) API
 */
export const userPromptsApi = {
  /**
   * Get all custom prompts for the current user
   */
  list: async (): Promise<UserPrompt[]> => {
    return fetchApi<UserPrompt[]>('/api/backend-da/user-prompts');
  },

  /**
   * Create a new custom prompt
   */
  create: async (data: CreateUserPromptRequest): Promise<UserPrompt> => {
    return fetchApi<UserPrompt>('/api/backend-da/user-prompts', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete a custom prompt
   */
  delete: async (promptId: string): Promise<{ message: string }> => {
    return fetchApi<{ message: string }>(`/api/backend-da/user-prompts?id=${promptId}`, {
      method: 'DELETE',
    });
  },
};

/**
 * System Prompts API
 */
export const systemPromptsApi = {
  /**
   * Get all system prompts
   */
  list: async (): Promise<SystemPrompt[]> => {
    return fetchApi<SystemPrompt[]>('/api/backend-da/system-prompts');
  },
};

/**
 * Auth API
 */
export const authApi = {
  /**
   * Check authentication status
   */
  status: async (): Promise<AuthStatus> => {
    return fetchApi<AuthStatus>('/api/backend-da/auth');
  },
};

/**
 * Models API
 */
export const modelsApi = {
  /**
   * Get all available models from all providers
   */
  listAll: async (): Promise<AllModelsResponse> => {
    return fetchApi<AllModelsResponse>('/api/backend-llm/models');
  },

  /**
   * Get featured/recommended models
   */
  listFeatured: async (): Promise<FeaturedModelsResponse> => {
    return fetchApi<FeaturedModelsResponse>('/api/backend-llm/models?featured=true');
  },
};

/**
 * Combined API client
 */
export const apiClient = {
  sessions: sessionsApi,
  prompts: promptsApi,
  chat: chatApi,
  quota: quotaApi,
  userPrompts: userPromptsApi,
  systemPrompts: systemPromptsApi,
  auth: authApi,
  models: modelsApi,
};
