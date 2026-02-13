/**
 * TypeScript type definitions for all BFF API endpoints
 * 
 * These types match the schemas from Backend-da and Backend-llm.
 * They are used throughout the application for type safety.
 */

/* eslint-disable @typescript-eslint/no-unused-vars */

/**
 * Chat Sessions
 */
export interface ChatSession {
  session_id: string;
  user_id: string;
  title: string;
  created_at: string;
}

export interface CreateSessionRequest {
  title: string;
}

/**
 * Chat Messages & History
 */
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface Prompt {
  prompt_id: string;
  user_id: string;
  session_id: string;
  prompt_text: string;
  llm_responses: string[];
  tokens_used?: number;
  timestamp: string;
}

export interface CreatePromptRequest {
  session_id: string;
  prompt_text: string;
  llm_responses: string[];
  tokens_used?: number;
}

/**
 * LLM Chat
 */
export type ModelProvider = 'openai' | 'google' | 'groq';

export type ModelName =
  // OpenAI (Latest: GPT-5 series)
  | 'gpt-5'
  | 'gpt-5-mini'
  | 'gpt-nano'
  // Google Gemini (Latest: 2.5 series)
  | 'gemini-2.5-pro'
  | 'gemini-2.5-flash'
  | 'gemini-2.5-flash-lite'
  // Groq LLaMA (Latest: 3.3 70B & 3.1 8B)
  | 'llama-3.3-70b-versatile'
  | 'llama-3.1-8b-instant';

/**
 * Model Discovery
 */
export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  description?: string;
  display_name?: string;
  created?: number;
  owned_by?: string;
  active?: boolean;
}

export interface AllModelsResponse {
  success: boolean;
  models: {
    openai: ModelInfo[];
    google: ModelInfo[];
    groq: ModelInfo[];
  };
  total_count: {
    openai: number;
    google: number;
    groq: number;
  };
}

export interface FeaturedModelsResponse {
  success: boolean;
  featured_models: {
    openai: ModelInfo[];
    google: ModelInfo[];
    groq: ModelInfo[];
  };
}

export interface ChatRequest {
  question: string;
  model: ModelName;
  provider: string; // Added provider
  session_id?: string;
  chat_history?: ChatMessage[];
  system_prompts?: string[];
}

export interface ChatResponse {
  answer: string | null;
  raw_response?: unknown;
  error_message?: string | null;
  session_id: string;
  model: string;
  provider: string;
  request_timestamp: string;
  response_timestamp: string;
  latency_ms: number;
  usage?: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
    // Gemini uses different names
    prompt_token_count?: number;
    candidates_token_count?: number;
    total_token_count?: number;
  };
}

/**
 * Streaming Chat
 */
export interface StreamChunk {
  token: string;
  chunk_type: 'content' | 'final';
  done: boolean;
  full_content?: string;
  usage?: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
    prompt_token_count?: number;
    candidates_token_count?: number;
    total_token_count?: number;
  };
  model?: string;
  provider?: string;
  session_id?: string;
}

/**
 * User Quota
 */
export interface Quota {
  user_id: string;
  daily_limit: number;
  used_today: number;
  last_reset: string | null;
  quota_remaining?: number; // Computed field
  reset_at?: string; // Computed field
}

/**
 * User Prompts (Custom Prompt Library)
 */
export interface UserPrompt {
  prompt_id: string;
  user_id: string;
  prompt_text: string;
}

export interface CreateUserPromptRequest {
  prompt_text: string;
}

/**
 * System Prompts
 */
export interface SystemPrompt {
  prompt_id: string;
  prompt_text: string;
}

/**
 * Auth Status
 */
export interface AuthStatus {
  authenticated: boolean;
  userId?: string;
  message: string;
}

/**
 * Error Response
 */
export interface ApiError {
  error: string;
  detail?: string;
}

/**
 * API Response wrapper for better error handling
 */
export type ApiResponse<T> = 
  | { success: true; data: T }
  | { success: false; error: ApiError };
