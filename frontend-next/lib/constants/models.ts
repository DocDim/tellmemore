/**
 * LLM Models Constants
 * 
 * These models are hardcoded based on Backend-llm/api/pydantic_models.py
 * Source of truth: Backend-llm ModelName enum
 * 
 * TODO: Create GET /api/backend-llm/models endpoint for dynamic fetching
 */

export enum ModelProvider {
  OPENAI = "openai",
  GOOGLE = "google",
  GROQ = "groq",
}

export interface Model {
  id: string;              // Model ID (e.g., "gpt-5")
  name: string;            // Display name (e.g., "GPT-5")
  provider: ModelProvider; // Provider enum
  description: string;     // Short description
  tier?: "flagship" | "mini" | "lite" | "instant"; // Model tier
}

/**
 * All available models
 * Matches Backend-llm/api/pydantic_models.py ModelName enum
 */
export const MODELS: Model[] = [
  // OpenAI Models
  {
    id: "gpt-5",
    name: "GPT-5",
    provider: ModelProvider.OPENAI,
    description: "Latest flagship model from OpenAI",
    tier: "flagship",
  },
  {
    id: "gpt-5-mini",
    name: "GPT-5 Mini",
    provider: ModelProvider.OPENAI,
    description: "Smaller, faster variant of GPT-5",
    tier: "mini",
  },
  {
    id: "gpt-nano",
    name: "GPT Nano",
    provider: ModelProvider.OPENAI,
    description: "Compact model for simple tasks",
    tier: "lite",
  },
  {
    id: "gpt-4o",
    name: "GPT-4o",
    provider: ModelProvider.OPENAI,
    description: "Omni model for complex tasks",
    tier: "flagship",
  },
  {
    id: "gpt-4o-mini",
    name: "GPT-4o Mini",
    provider: ModelProvider.OPENAI,
    description: "Small and fast model for simple tasks",
    tier: "mini",
  },
  
  // Google Gemini Models
  {
    id: "gemini-2.5-pro",
    name: "Gemini 2.5 Pro",
    provider: ModelProvider.GOOGLE,
    description: "Google's most capable model",
    tier: "flagship",
  },
  {
    id: "gemini-2.5-flash",
    name: "Gemini 2.5 Flash",
    provider: ModelProvider.GOOGLE,
    description: "Fast and efficient Gemini model",
    tier: "instant",
  },
  {
    id: "gemini-2.5-flash-lite",
    name: "Gemini 2.5 Flash Lite",
    provider: ModelProvider.GOOGLE,
    description: "Lightweight Gemini variant",
    tier: "lite",
  },
  
  // Groq LLaMA Models
  {
    id: "llama-3.3-70b-versatile",
    name: "LLaMA 3.3 70B",
    provider: ModelProvider.GROQ,
    description: "Powerful open-source model (70B params)",
    tier: "flagship",
  },
  {
    id: "llama-3.1-8b-instant",
    name: "LLaMA 3.1 8B",
    provider: ModelProvider.GROQ,
    description: "Fast 8B parameter model",
    tier: "instant",
  },
];

/**
 * Get models filtered by provider
 */
export function getModelsByProvider(provider: ModelProvider): Model[] {
  return MODELS.filter((m) => m.provider === provider);
}

/**
 * Get model by ID
 */
export function getModelById(id: string): Model | undefined {
  return MODELS.find((m) => m.id === id);
}

/**
 * Default model selections for left/right chat
 */
export const DEFAULT_LEFT_MODEL = "gpt-5";
export const DEFAULT_RIGHT_MODEL = "gemini-2.5-flash";

/**
 * Provider display names
 */
export const PROVIDER_NAMES: Record<ModelProvider, string> = {
  [ModelProvider.OPENAI]: "OpenAI",
  [ModelProvider.GOOGLE]: "Google",
  [ModelProvider.GROQ]: "Groq",
};

/**
 * Provider colors for badges (Tailwind classes)
 */
export const PROVIDER_COLORS: Record<ModelProvider, string> = {
  [ModelProvider.OPENAI]: "bg-green-500/10 text-green-500 border-green-500/20",
  [ModelProvider.GOOGLE]: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  [ModelProvider.GROQ]: "bg-purple-500/10 text-purple-500 border-purple-500/20",
};
