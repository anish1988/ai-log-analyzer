"use client";

import {
  useCallback,
  useState,
} from "react";

import type {
  AIAnalysisRequest,
  AIAnalysisResponse,
} from "@/lib/types/aiAnalysis";


// =============================================================================
// STATE TYPE
// =============================================================================

interface UseAIAnalysisState {
  data: AIAnalysisResponse | null;

  loading: boolean;

  error: string | null;
}


// =============================================================================
// HOOK RETURN TYPE
// =============================================================================

interface UseAIAnalysisReturn
  extends UseAIAnalysisState {

  analyze: (
    request: AIAnalysisRequest,
  ) => Promise<AIAnalysisResponse | null>;

  reset: () => void;
}


// =============================================================================
// API URL
// =============================================================================

const API_URL =
  process.env.NEXT_PUBLIC_API_URL;


// =============================================================================
// HOOK
// =============================================================================

export function useAIAnalysis(): UseAIAnalysisReturn {

  const [
    data,
    setData,
  ] = useState<AIAnalysisResponse | null>(
    null,
  );


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  );


  // ===========================================================================
  // ANALYZE
  // ===========================================================================

  const analyze = useCallback(
    async (
      request: AIAnalysisRequest,
    ): Promise<AIAnalysisResponse | null> => {

      // -----------------------------------------------------------------------
      // Validate API configuration
      // -----------------------------------------------------------------------

      if (!API_URL) {

        const message =
          "NEXT_PUBLIC_API_URL is not configured.";

        setError(message);

        return null;
      }


      // -----------------------------------------------------------------------
      // Validate request
      // -----------------------------------------------------------------------

      if (
        !request.selected_errors ||
        request.selected_errors.length === 0
      ) {

        const message =
          "At least one error is required for AI analysis.";

        setError(message);

        return null;
      }


      // -----------------------------------------------------------------------
      // Start request
      // -----------------------------------------------------------------------

      setLoading(true);

      setError(null);


      try {

        // ---------------------------------------------------------------------
        // API request
        // ---------------------------------------------------------------------

        const response =
          await fetch(
            `${API_URL}/api/ai/analyze`,
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",
              },

              body:
                JSON.stringify(request),
            },
          );


        // ---------------------------------------------------------------------
        // HTTP error
        // ---------------------------------------------------------------------

        if (!response.ok) {

          let message =
            "AI analysis failed.";

          try {

            const errorBody =
              await response.json();

            if (
              typeof errorBody?.detail ===
              "string"
            ) {

              message =
                errorBody.detail;
            }

          } catch {

            // Keep the default message
            // when the response is not JSON.
          }


          throw new Error(
            message,
          );
        }


        // ---------------------------------------------------------------------
        // Parse response
        // ---------------------------------------------------------------------

        const result =
          (await response.json()) as
          AIAnalysisResponse;


        // ---------------------------------------------------------------------
        // Store result
        // ---------------------------------------------------------------------

        setData(result);


        return result;

      } catch (err) {

        // ---------------------------------------------------------------------
        // Normalize error
        // ---------------------------------------------------------------------

        const message =
          err instanceof Error
            ? err.message
            : "AI analysis failed.";


        setError(message);


        return null;

      } finally {

        setLoading(false);
      }
    },
    [],
  );


  // ===========================================================================
  // RESET
  // ===========================================================================

  const reset = useCallback(
    () => {

      setData(null);

      setLoading(false);

      setError(null);
    },
    [],
  );


  // ===========================================================================
  // RETURN
  // ===========================================================================

  return {
    data,

    loading,

    error,

    analyze,

    reset,
  };
}