"use client";

import {
  useCallback,
} from "react";

import {
  useAIAnalysis,
} from "@/hooks/useAIAnalysis";

import type {
  AIAnalysisResponse,
  AISelectedError,
} from "@/lib/types/aiAnalysis";


// =============================================================================
// PROPS
// =============================================================================

interface AIAnalysisLauncherProps {
  selectedErrors: AISelectedError[];

  requestId?: string;

  metadata?: Record<string, unknown>;

  onStarted?: () => void;

  onCompleted?: (
    response: AIAnalysisResponse,
  ) => void;

  onError?: (
    error: string,
  ) => void;
}


// =============================================================================
// COMPONENT
// =============================================================================

export default function AIAnalysisLauncher({
  selectedErrors,
  requestId,
  metadata,
  onStarted,
  onCompleted,
  onError,
}: AIAnalysisLauncherProps) {

  const {
    analyze,
    loading,
    error,
  } = useAIAnalysis();


  // ===========================================================================
  // START ANALYSIS
  // ===========================================================================

  const startAnalysis = useCallback(
    async () => {

      if (
        selectedErrors.length === 0
      ) {

        const message =
          "Please select at least one error for AI analysis.";

        onError?.(message);

        return;
      }


      onStarted?.();


      const response =
        await analyze({
          request_id:
            requestId ?? null,

          selected_errors:
            selectedErrors,

          metadata,
        });


      if (response) {

        onCompleted?.(
          response,
        );

        return;
      }


      if (error) {

        onError?.(
          error,
        );
      }

    },
    [
      analyze,
      error,
      metadata,
      onCompleted,
      onError,
      onStarted,
      requestId,
      selectedErrors,
    ],
  );


  // ===========================================================================
  // UI
  // ===========================================================================

  return (
    <button
      type="button"
      disabled={
        loading ||
        selectedErrors.length === 0
      }
      onClick={startAnalysis}
      className={`
        inline-flex
        items-center
        gap-2
        rounded-lg
        px-6
        py-2.5
        text-sm
        font-semibold
        text-white
        transition
        ${
          loading ||
          selectedErrors.length === 0
            ? "cursor-not-allowed bg-indigo-300"
            : "bg-indigo-600 hover:bg-indigo-700"
        }
      `}
    >

      {loading ? (
        <>
          <span
            className="
              h-4
              w-4
              animate-spin
              rounded-full
              border-2
              border-white
              border-t-transparent
            "
          />

          Analyzing...
        </>
      ) : (
        <>
          ✨ Analyze with AI

          {selectedErrors.length > 0 &&
            ` (${selectedErrors.length})`}
        </>
      )}

    </button>
  );
}