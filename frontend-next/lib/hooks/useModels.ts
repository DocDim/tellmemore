/**
 * useModels Hook
 * 
 * Fetches available LLM models from Backend-llm via BFF layer.
 * Uses React Query for caching and automatic refetching.
 */

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { Model, ModelProvider } from '@/lib/constants/models';
import type { FeaturedModelsResponse } from '@/lib/api/types';

/**
 * Query keys for models
 */
export const modelKeys = {
  all: ['models'] as const,
  featured: ['models', 'featured'] as const,
};

/**
 * Hook to get all available LLM models
 * 
 * Fetches from GET /api/backend-llm/models
 * Returns all models dynamically discovered from provider APIs
 * Caches for 1 hour (models don't change often)
 * 
 * @example
 * ```tsx
 * const { data: models, isLoading, error } = useModels();
 * if (models) {
 *   console.log(models); // Array of Model objects
 * }
 * ```
 */
export function useModels() {
  return useQuery({
    queryKey: modelKeys.all,
    queryFn: async () => {
      const response = await apiClient.models.listAll();
      
      // Transform backend response to frontend Model format
      const models: Model[] = [];
      
      // Add OpenAI models
      response.models.openai.forEach((m) => {
        models.push({
          id: m.id,
          name: m.name,
          provider: ModelProvider.OPENAI,
          description: m.description || '',
        });
      });
      
      // Add Google models
      response.models.google.forEach((m) => {
        models.push({
          id: m.id,
          name: m.name,
          provider: ModelProvider.GOOGLE,
          description: m.description || '',
        });
      });
      
      // Add Groq models
      response.models.groq.forEach((m) => {
        models.push({
          id: m.id,
          name: m.name,
          provider: ModelProvider.GROQ,
          description: m.description || '',
        });
      });
      
      return models;
    },
    // Cache for 1 hour
    staleTime: 1000 * 60 * 60,
    gcTime: 1000 * 60 * 60 * 24,
    retry: 2,
  });
}

/**
 * Hook to get only featured/recommended models
 * 
 * Fetches from GET /api/backend-llm/models?featured=true
 * Returns curated list of recommended models for cleaner UX
 * Useful when you want a smaller, handpicked selection
 * 
 * @example
 * ```tsx
 * const { data: featuredModels } = useFeaturedModels();
 * ```
 */
export function useFeaturedModels() {
  return useQuery({
    queryKey: modelKeys.featured,
    queryFn: async () => {
      const response = await apiClient.models.listFeatured();
      
      // Transform backend response to frontend Model format
      const models: Model[] = [];
      
      // Add OpenAI models
      response.featured_models.openai.forEach((m) => {
        models.push({
          id: m.id,
          name: m.name,
          provider: ModelProvider.OPENAI,
          description: m.description || '',
        });
      });
      
      // Add Google models
      response.featured_models.google.forEach((m) => {
        models.push({
          id: m.id,
          name: m.name,
          provider: ModelProvider.GOOGLE,
          description: m.description || '',
        });
      });
      
      // Add Groq models
      response.featured_models.groq.forEach((m) => {
        models.push({
          id: m.id,
          name: m.name,
          provider: ModelProvider.GROQ,
          description: m.description || '',
        });
      });
      
      return models;
    },
    staleTime: 3600000, // 1 hour
    retry: 2,
  });
}
