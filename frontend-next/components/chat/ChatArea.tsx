"use client";

import { useRef, useEffect } from "react";
import { ChatMessage } from "./ChatMessage";
import { ModelSelector } from "./ModelSelector";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  model?: string;
  timestamp: Date;
  isLoading?: boolean;
  isStreaming?: boolean; // True while actively streaming
  error?: string;
}

interface ChatAreaProps {
  model: string;
  messages: Message[];
  isLoading?: boolean;
  error?: string;
  onModelChange: (model: string) => void;
  excludeModel?: string; // Model to exclude from selection (for dual chat)
  hideHeader?: boolean; // Hide the header with model selector (when shown externally)
}

export function ChatArea({
  model,
  messages,
  isLoading,
  error,
  onModelChange,
  excludeModel,
  hideHeader = false,
}: ChatAreaProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]); // Also scroll when loading state changes

  return (
    <div className={cn(
      "flex min-h-0 flex-1 flex-col overflow-hidden",
      "bg-card text-card-foreground rounded-3xl border shadow-sm"
    )}>
      {/* Header with Model Selector - Right aligned, pill-shaped */}
      {!hideHeader && (
        <div className="flex shrink-0 items-center justify-end border-b px-1 py-1">
          <div className="w-auto">
            <ModelSelector
              value={model}
              onValueChange={onModelChange}
              excludeModel={excludeModel}
            />
          </div>
        </div>
      )}

      {/* Messages area - scrolls independently, takes all available space */}
      <div className="flex-1 overflow-y-auto p-2" ref={scrollRef}>
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center p-8">
            <div className="text-center text-muted-foreground">
              <p className="text-sm">No messages yet</p>
              <p className="mt-1 text-xs">
                Start a conversation with {model}
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                role={message.role}
                content={message.content}
                timestamp={message.timestamp}
                model={message.model}
                isLoading={message.isLoading}
                error={message.error}
              />
            ))}
            
            {/* Show loading indicator if waiting for assistant response */}
            {isLoading && messages[messages.length - 1]?.role === 'user' && (
              <div className="flex w-full gap-3 px-2 py-2">
                <div className="flex max-w-[80%] flex-col gap-2 items-start">
                  {/* Header: Model badge + loading indicator */}
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Badge variant="outline" className="text-xs">
                      {model}
                    </Badge>
                    <Loader2 className="h-3 w-3 animate-spin" />
                    <span>Thinking...</span>
                  </div>
                  
                  {/* Loading bubble */}
                  <div className="rounded-lg bg-muted px-4 py-3">
                    <div className="flex items-center gap-1">
                      <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-pulse" />
                      <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-pulse [animation-delay:75ms]" />
                      <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-pulse [animation-delay:150ms]" />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Error display */}
      {error && (
        <div className="shrink-0 border-t p-4">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
}

// Loading skeleton for ChatArea
export function ChatAreaSkeleton() {
  return (
    <div className={cn(
      "flex min-h-0 flex-1 flex-col overflow-hidden",
      "bg-card text-card-foreground rounded-3xl border shadow-sm"
    )}>
      {/* Header skeleton */}
      <div className="flex shrink-0 items-center justify-end border-b px-1 py-1">
        <Skeleton className="h-9 w-48 rounded-full" />
      </div>

      {/* Messages skeleton - chat bubble sized */}
      <div className="flex-1 p-2">
        <div className="flex flex-col gap-1">
          {/* User message skeleton (right aligned) */}
          <div className="flex justify-end">
            <Skeleton className="h-16 w-3/4 max-w-md rounded-2xl" />
          </div>
          {/* Assistant message skeleton (left aligned) */}
          <div className="flex justify-start">
            <Skeleton className="h-20 w-4/5 max-w-lg rounded-2xl" />
          </div>
          {/* Another user message */}
          <div className="flex justify-end">
            <Skeleton className="h-12 w-2/3 max-w-sm rounded-2xl" />
          </div>
        </div>
      </div>
    </div>
  );
}

