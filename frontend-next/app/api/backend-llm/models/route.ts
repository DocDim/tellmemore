/**
 * BFF API Route: LLM Models Discovery
 * 
 * Proxies model discovery requests to Backend-llm.
 * Returns available models from all providers (OpenAI, Google, Groq).
 * 
 * Endpoints:
 * - GET /api/backend-llm/models - Get all available models
 * - GET /api/backend-llm/models/featured - Get featured/recommended models
 */

import { NextRequest, NextResponse } from 'next/server';
import { env } from '@/lib/env';

/**
 * TypeScript types matching Backend-llm response
 */
interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  description?: string;
  display_name?: string;
  created?: number;
  owned_by?: string;
  active?: boolean;
}

interface AllModelsResponse {
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

interface FeaturedModelsResponse {
  success: boolean;
  featured_models: {
    openai: ModelInfo[];
    google: ModelInfo[];
    groq: ModelInfo[];
  };
}

interface ErrorResponse {
  error: string;
  detail?: string;
}

/**
 * GET /api/backend-llm/models
 * 
 * Get all available models or featured models based on query parameter.
 * 
 * Query Parameters:
 * - featured: boolean (optional) - If true, returns only featured/recommended models
 * 
 * Response:
 * - 200: AllModelsResponse | FeaturedModelsResponse
 * - 500: Internal server error
 * - 502: Bad gateway (Backend-llm service error)
 */
export async function GET(request: NextRequest): Promise<NextResponse<AllModelsResponse | FeaturedModelsResponse | ErrorResponse>> {
  try {
    // Check if featured models are requested
    const { searchParams } = new URL(request.url);
    const featured = searchParams.get('featured') === 'true';
    
    const endpoint = featured ? '/models/featured' : '/models';
    const backendUrl = `${env.server.backendLlmUrl}${endpoint}`;
    
    // Fetch from Backend-llm
    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Cache for 1 hour since models don't change often
      next: { revalidate: 3600 },
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[BFF Models] Backend-llm error (${response.status}):`, errorText);
      
      return NextResponse.json(
        {
          error: 'Failed to fetch models from LLM service',
          detail: `Backend-llm returned ${response.status}`,
        } satisfies ErrorResponse,
        { status: 502 }
      );
    }
    
    const data = await response.json();
    
    // Return the models data
    return NextResponse.json(data, {
      headers: {
        'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=7200',
      },
    });
    
  } catch (error) {
    console.error('[BFF Models] Error fetching models:', error);
    
    return NextResponse.json(
      {
        error: 'Internal server error',
        detail: error instanceof Error ? error.message : 'Unknown error',
      } satisfies ErrorResponse,
      { status: 500 }
    );
  }
}
