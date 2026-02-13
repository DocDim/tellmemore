/**
 * ModelSelector Component
 * 
 * Dropdown selector for LLM models with provider grouping and search.
 * Prevents selecting the same model on both sides (left/right chat).
 */

'use client';

import { Check, ChevronsUpDown, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { useModels } from '@/lib/hooks';
import {
  ModelProvider,
  PROVIDER_NAMES,
  PROVIDER_COLORS,
  getModelById,
  getModelsByProvider,
} from '@/lib/constants/models';
import { useState } from 'react';

interface ModelSelectorProps {
  value: string;          // Current model ID
  onValueChange: (modelId: string) => void;
  excludeModel?: string;  // Don't allow selecting this model (for preventing duplicates)
}

export function ModelSelector({ 
  value, 
  onValueChange, 
  excludeModel,
}: ModelSelectorProps) {
  const [open, setOpen] = useState(false);
  const { data: models, isLoading } = useModels();

  // Find selected model from fetched data or fallback to constants
  const selectedModel = models?.find((m) => m.id === value) || getModelById(value);

  // Group models by provider from fetched data
  const openaiModels = (models || [])
    .filter((m) => m.provider === ModelProvider.OPENAI && m.id !== excludeModel);
  const googleModels = (models || [])
    .filter((m) => m.provider === ModelProvider.GOOGLE && m.id !== excludeModel);
  const groqModels = (models || [])
    .filter((m) => m.provider === ModelProvider.GROQ && m.id !== excludeModel);
  
  console.log('[ModelSelector] Models by provider:', {
    openai: openaiModels.length,
    google: googleModels.length,
    groq: groqModels.length,
    total: (models || []).length,
    excluded: excludeModel,
  });

  if (isLoading) {
    return (
      <Button variant="outline" className="w-full justify-start" disabled>
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        Loading models...
      </Button>
    );
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="justify-between rounded-full px-4"
        >
          {selectedModel ? (
            <div className="flex items-center gap-2">
              <Badge 
                variant="outline" 
                className={cn(
                  "text-xs font-medium rounded-full",
                  PROVIDER_COLORS[selectedModel.provider]
                )}
              >
                {PROVIDER_NAMES[selectedModel.provider]}
              </Badge>
              <span className="truncate">{selectedModel.name}</span>
            </div>
          ) : (
            <span className="text-muted-foreground">Select model...</span>
          )}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[400px] p-0" align="end">
        <Command>
          <CommandInput placeholder="Search models..." />
          <CommandEmpty>No models found.</CommandEmpty>
          <CommandList className="max-h-[400px]">
            {/* OpenAI Models */}
            {openaiModels.length > 0 && (
              <CommandGroup heading="OpenAI">
                {openaiModels.map((model) => (
                  <CommandItem
                    key={model.id}
                    value={model.id}
                    onSelect={(currentValue: string) => {
                      onValueChange(currentValue);
                      setOpen(false);
                    }}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        value === model.id ? "opacity-100" : "opacity-0"
                      )}
                    />
                    <div className="flex flex-col gap-1 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{model.name}</span>
                        {model.tier && (
                          <Badge variant="secondary" className="text-xs">
                            {model.tier}
                          </Badge>
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {model.description}
                      </span>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}

            {/* Google Gemini Models */}
            {googleModels.length > 0 && (
              <CommandGroup heading="Google Gemini">
                {googleModels.map((model) => (
                  <CommandItem
                    key={model.id}
                    value={model.id}
                    onSelect={(currentValue: string) => {
                      onValueChange(currentValue);
                      setOpen(false);
                    }}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        value === model.id ? "opacity-100" : "opacity-0"
                      )}
                    />
                    <div className="flex flex-col gap-1 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{model.name}</span>
                        {model.tier && (
                          <Badge variant="secondary" className="text-xs">
                            {model.tier}
                          </Badge>
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {model.description}
                      </span>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}

            {/* Groq LLaMA Models */}
            {groqModels.length > 0 && (
              <CommandGroup heading="Groq LLaMA">
                {groqModels.map((model) => (
                  <CommandItem
                    key={model.id}
                    value={model.id}
                    onSelect={(currentValue: string) => {
                      onValueChange(currentValue);
                      setOpen(false);
                    }}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        value === model.id ? "opacity-100" : "opacity-0"
                      )}
                    />
                    <div className="flex flex-col gap-1 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{model.name}</span>
                        {model.tier && (
                          <Badge variant="secondary" className="text-xs">
                            {model.tier}
                          </Badge>
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {model.description}
                      </span>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
