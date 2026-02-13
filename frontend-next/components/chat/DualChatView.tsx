"use client";

import { useState, useMemo, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { ChatArea, ChatAreaSkeleton } from "./ChatArea";
import { ChatInput } from "./ChatInput";
import { useChatStore } from "@/lib/stores/chatStore";
import { usePromptsStore } from "@/lib/stores/promptsStore";
import { useChatHistory, useSavePrompt, promptKeys } from "@/lib/hooks/usePrompts";
import { useUpdateSession, useSession } from "@/lib/hooks/useSessions";
import { useSystemPrompts, useQuota, useModels } from "@/lib/hooks";
import { apiClient } from "@/lib/api/client";
import { toast } from "sonner";
import type { Prompt, StreamChunk } from "@/lib/api/types";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  model?: string; // For assistant messages, which model generated it
  isStreaming?: boolean; // True while streaming is in progress
}

interface DualChatViewProps {
  sessionId: string | null;
}

/**
 * Truncate text to a maximum length and add ellipsis
 */
function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + "...";
}

export function DualChatView({ sessionId }: DualChatViewProps) {
  const { leftModel, rightModel, setLeftModel, setRightModel } = useChatStore();
  const { getSelectedSystemPromptTexts } = usePromptsStore();
  const [isLoadingLeft, setIsLoadingLeft] = useState(false);
  const [isLoadingRight, setIsLoadingRight] = useState(false);
  const [errorLeft, setErrorLeft] = useState<string | undefined>();
  const [errorRight, setErrorRight] = useState<string | undefined>();
  const [hasShownWarning, setHasShownWarning] = useState(false);

  // Streaming state: temporary messages being streamed (not in cache yet)
  const [streamingLeft, setStreamingLeft] = useState<string>("");
  const [streamingRight, setStreamingRight] = useState<string>("");

  // React Query hooks
  const queryClient = useQueryClient();
  const savePrompt = useSavePrompt();
  const updateSession = useUpdateSession();

  // Fetch current session info for breadcrumb
  const { data: currentSession } = useSession(sessionId);

  // Fetch system prompts for context
  const { data: systemPrompts } = useSystemPrompts();

  // Fetch user quota for enforcement
  const { data: quota } = useQuota();

  // Fetch available models for provider lookup
  const { data: models } = useModels();

  // Calculate quota percentage
  const quotaPercentage = quota
    ? Math.round((quota.used_today / quota.daily_limit) * 100)
    : 0;

  const isQuotaExceeded = quotaPercentage >= 100;
  const isQuotaNearLimit = quotaPercentage >= 80 && quotaPercentage < 100;

  // Show warning toast when quota reaches 80% (only once per session)
  useEffect(() => {
    if (isQuotaNearLimit && !hasShownWarning && quota) {
      toast.warning("Quota Warning", {
        description: `You've used ${quota.used_today.toLocaleString()} of ${quota.daily_limit.toLocaleString()} tokens (${quotaPercentage}%). Your quota resets daily.`,
        duration: 10000,
      });
      setHasShownWarning(true);
    }
  }, [isQuotaNearLimit, hasShownWarning, quota, quotaPercentage]);

  // Fetch chat history for current session (React Query manages caching)
  const { data: prompts, isLoading: isLoadingHistory } = useChatHistory(
    sessionId || ""
  );

  // Debug: Log prompts data
  // console.log('📝 Chat history data:', {
  //   sessionId,
  //   promptsCount: prompts?.length || 0,
  //   prompts: prompts?.map(p => ({
  //     id: p.prompt_id,
  //     text: p.prompt_text.slice(0, 30),
  //     responsesCount: p.llm_responses?.length || 0,
  //     responses: p.llm_responses,
  //   })),
  // });

  // Convert prompts to messages (compute once per prompts change)
  // This is the source of truth for chat history - no local state needed!
  const { leftMessages, rightMessages } = useMemo(() => {
    if (!prompts || prompts.length === 0) {
      return { leftMessages: [], rightMessages: [] };
    }

    // Sort prompts by timestamp (oldest first) to ensure chronological order
    const sortedPrompts = [...prompts].sort((a, b) => {
      return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
    });

    // Build message arrays from prompts
    const leftMsgs: Message[] = [];
    const rightMsgs: Message[] = [];

    sortedPrompts.forEach((prompt: Prompt) => {
      // Add user message to both chats
      const userMsg: Message = {
        id: `user-${prompt.prompt_id}`,
        role: "user",
        content: prompt.prompt_text,
        timestamp: new Date(prompt.timestamp),
      };
      leftMsgs.push(userMsg);
      rightMsgs.push(userMsg);

      // Add assistant responses if available
      if (prompt.llm_responses && prompt.llm_responses.length > 0) {
        // First response goes to left chat
        if (prompt.llm_responses[0]) {
          leftMsgs.push({
            id: `assistant-left-${prompt.prompt_id}`,
            role: "assistant",
            content: prompt.llm_responses[0],
            timestamp: new Date(prompt.timestamp),
            model: leftModel, // TODO: Store actual model used
          });
        }
        // Second response goes to right chat (if dual chat)
        if (prompt.llm_responses[1]) {
          rightMsgs.push({
            id: `assistant-right-${prompt.prompt_id}`,
            role: "assistant",
            content: prompt.llm_responses[1],
            timestamp: new Date(prompt.timestamp),
            model: rightModel, // TODO: Store actual model used
          });
        }
      }
    });

    // Add streaming messages if currently streaming
    if (isLoadingLeft && streamingLeft) {
      leftMsgs.push({
        id: "streaming-left",
        role: "assistant",
        content: streamingLeft,
        timestamp: new Date(),
        model: leftModel,
        isStreaming: true,
      });
    }

    if (isLoadingRight && streamingRight) {
      rightMsgs.push({
        id: "streaming-right",
        role: "assistant",
        content: streamingRight,
        timestamp: new Date(),
        model: rightModel,
        isStreaming: true,
      });
    }

    return { leftMessages: leftMsgs, rightMessages: rightMsgs };
  }, [prompts, leftModel, rightModel, isLoadingLeft, isLoadingRight, streamingLeft, streamingRight]);

  // Debug: Log converted messages
  // console.log('💬 Converted messages:', {
  //   leftCount: leftMessages.length,
  //   rightCount: rightMessages.length,
  //   leftMessages,
  //   rightMessages,
  // });

  // Single handler that streams from BOTH models simultaneously
  const handleSend = async (message: string) => {
    if (!sessionId) {
      console.error("Cannot send message without session ID");
      return;
    }

    // Check quota before sending
    if (isQuotaExceeded) {
      toast.error("Quota Exceeded", {
        description: "You've reached your daily quota limit. Your quota will reset in 24 hours.",
        duration: 10000,
      });
      return;
    }

    // STEP 1: IMMEDIATELY add user message to cache (optimistic update)
    const queryKey = promptKeys.list(sessionId);
    const optimisticMessage: Prompt = {
      prompt_id: 'temp-' + Date.now(),
      user_id: 'temp',
      session_id: sessionId,
      prompt_text: message,
      llm_responses: [], // Will be filled when streams complete
      timestamp: new Date().toISOString(),
    };

    queryClient.setQueryData<Prompt[]>(queryKey, (old: Prompt[] | undefined) => {
      return [...(old || []), optimisticMessage];
    });

    // Reset streaming state
    setStreamingLeft("");
    setStreamingRight("");
    setIsLoadingLeft(true);
    setIsLoadingRight(true);
    setErrorLeft(undefined);
    setErrorRight(undefined);

    try {
      // Auto-update session title if this is the first message
      const isFirstMessage = !prompts || prompts.length === 0;
      if (isFirstMessage && currentSession) {
        const title = truncate(message, 50);
        updateSession.mutate({
          sessionId,
          data: { title },
        });
      }

      // Get selected system prompts
      const selectedSystemPrompts = getSelectedSystemPromptTexts(systemPrompts || []);

      // STEP 2: Stream from both models in parallel
      const [leftResult, rightResult] = await Promise.allSettled([
        // Left model stream
        (async () => {
          let fullContent = "";
          let usage: StreamChunk['usage'] | undefined;

          try {
            // Lookup provider from models list
            const leftProvider = models?.find(m => m.id === leftModel)?.provider || 'openai';
            
            const stream = apiClient.chat.sendStream({
              question: message,
              model: leftModel as import("@/lib/api/types").ModelName,
              provider: leftProvider,
              session_id: sessionId,
              system_prompts: selectedSystemPrompts,
            });

            for await (const chunk of stream) {
              if (chunk.chunk_type === 'content') {
                fullContent += chunk.token;
                setStreamingLeft(fullContent); // Update UI incrementally
              } else if (chunk.chunk_type === 'final' && chunk.done) {
                fullContent = chunk.full_content || fullContent;
                usage = chunk.usage;
                setStreamingLeft(fullContent); // Final update
              }
            }

            return { content: fullContent, usage };
          } catch (error) {
            console.error('Left model streaming error:', error);
            throw error;
          }
        })(),
        // Right model stream
        (async () => {
          let fullContent = "";
          let usage: StreamChunk['usage'] | undefined;

          try {
            // Lookup provider from models list
            const rightProvider = models?.find(m => m.id === rightModel)?.provider || 'openai';

            const stream = apiClient.chat.sendStream({
              question: message,
              model: rightModel as import("@/lib/api/types").ModelName,
              provider: rightProvider,
              session_id: sessionId,
              system_prompts: selectedSystemPrompts,
            });

            for await (const chunk of stream) {
              if (chunk.chunk_type === 'content') {
                fullContent += chunk.token;
                setStreamingRight(fullContent); // Update UI incrementally
              } else if (chunk.chunk_type === 'final' && chunk.done) {
                fullContent = chunk.full_content || fullContent;
                usage = chunk.usage;
                setStreamingRight(fullContent); // Final update
              }
            }

            return { content: fullContent, usage };
          } catch (error) {
            console.error('Right model streaming error:', error);
            throw error;
          }
        })(),
      ]);

      // STEP 3: Collect responses and token counts
      const responses: string[] = [];
      let totalTokens = 0;

      // Handle left model result
      if (leftResult.status === "fulfilled") {
        const { content, usage } = leftResult.value;
        responses.push(content);
        if (usage) {
          const tokens = usage.total_tokens || usage.total_token_count || 0;
          totalTokens += tokens;
        }
      } else {
        console.error('Left model failed:', leftResult.reason);
        setErrorLeft(leftResult.reason?.message || "Streaming failed");
        responses.push(""); // Placeholder
      }

      // Handle right model result
      if (rightResult.status === "fulfilled") {
        const { content, usage } = rightResult.value;
        responses.push(content);
        if (usage) {
          const tokens = usage.total_tokens || usage.total_token_count || 0;
          totalTokens += tokens;
        }
      } else {
        console.error('Right model failed:', rightResult.reason);
        setErrorRight(rightResult.reason?.message || "Streaming failed");
        responses.push(""); // Placeholder
      }

      // STEP 4: Update cache with final responses (replace optimistic message)
      queryClient.setQueryData<Prompt[]>(queryKey, (old: Prompt[] | undefined) => {
        if (!old || old.length === 0) return old;
        
        const lastMessage = old[old.length - 1];
        if (lastMessage && lastMessage.prompt_text === message) {
          return [
            ...old.slice(0, -1),
            {
              ...lastMessage,
              llm_responses: responses,
            },
          ];
        }
        return old;
      });

      // STEP 5: Save to backend
      await savePrompt.mutateAsync({
        session_id: sessionId,
        prompt_text: message,
        llm_responses: responses,
        tokens_used: totalTokens,
      });

      // Clear streaming state after successful save
      setStreamingLeft("");
      setStreamingRight("");
    } catch (error) {
      console.error("Failed to send message:", error);
      const errorMsg = error instanceof Error ? error.message : "Failed to send message";
      setErrorLeft(errorMsg);
      setErrorRight(errorMsg);
      
      // Rollback: Remove optimistic message on error
      queryClient.setQueryData<Prompt[]>(queryKey, (old: Prompt[] | undefined) => {
        if (!old || old.length === 0) return old;
        const lastMessage = old[old.length - 1];
        if (lastMessage && lastMessage.prompt_text === message && lastMessage.prompt_id.startsWith('temp-')) {
          return old.slice(0, -1);
        }
        return old;
      });

      // Clear streaming state on error
      setStreamingLeft("");
      setStreamingRight("");
    } finally {
      setIsLoadingLeft(false);
      setIsLoadingRight(false);
    }
  };

  if (!sessionId) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center text-muted-foreground">
          <p className="text-lg font-medium">No session selected</p>
          <p className="mt-2 text-sm">
            Create a new session or select an existing one to start chatting
          </p>
        </div>
      </div>
    );
  }

  if (isLoadingHistory) {
    return (
      <div className="grid h-full grid-cols-2 gap-4">
        <ChatAreaSkeleton />
        <ChatAreaSkeleton />
      </div>
    );
  }

  const isLoading = isLoadingLeft || isLoadingRight;

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {/* Dual chat areas - grid takes remaining space */}
      {/* CRITICAL: grid has flex-1 min-h-0 but NO overflow-hidden! */}
      <div className="grid flex-1 grid-cols-2 gap-4 p-4 min-h-0">
        <ChatArea
          model={leftModel}
          messages={leftMessages}
          isLoading={isLoadingLeft}
          error={errorLeft}
          onModelChange={setLeftModel}
          excludeModel={rightModel}
        />
        <ChatArea
          model={rightModel}
          messages={rightMessages}
          isLoading={isLoadingRight}
          error={errorRight}
          onModelChange={setRightModel}
          excludeModel={leftModel}
        />
      </div>

      {/* Single input at bottom - fixed position */}
      <div className="shrink-0 border-t bg-background">
        <ChatInput
          onSend={handleSend}
          isLoading={isLoading}
          placeholder={`Ask ${leftModel} and ${rightModel}...`}
        />
      </div>
    </div>
  );
}
