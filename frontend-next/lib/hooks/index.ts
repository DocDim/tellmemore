/**
 * React Query Hooks Index
 * 
 * Centralized export for all React Query hooks.
 * 
 * Usage:
 * ```tsx
 * import { useSessions, useCreateSession, useSendChat } from '@/lib/hooks';
 * ```
 */

// Session hooks
export {
  useSessions,
  useSession,
  useCreateSession,
  useUpdateSession,
  useDeleteSession,
  sessionKeys,
} from './useSessions';

// Chat history hooks
export {
  useChatHistory,
  useSavePrompt,
  promptKeys,
} from './usePrompts';

// User prompts (library) hooks
export {
  useUserPrompts,
  useCreateUserPrompt,
  useDeleteUserPrompt,
  userPromptKeys,
} from './useUserPrompts';

// System prompts hooks
export {
  useSystemPrompts,
  systemPromptKeys,
} from './useSystemPrompts';

// LLM chat hooks
export {
  useSendChat,
} from './useChat';

// Models hooks
export {
  useModels,
  modelKeys,
} from './useModels';

// Quota hooks
export {
  useQuota,
  quotaKeys,
} from './useQuota';

// Auth hooks
export {
  useAuthStatus,
  authKeys,
} from './useAuth';
