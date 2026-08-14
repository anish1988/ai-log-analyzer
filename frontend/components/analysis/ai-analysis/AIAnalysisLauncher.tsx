"use client";

import { useCallback, useState } from "react";

import useAIAnalysisProgress, {
  type AIProgressEvent,
} from "@/hooks/useAIAnalysisProgress";

import type {
  AISelectedError,
  AIAnalysisResponse,
} from "@/lib/types/aiAnalysis";

import AIAnalysisProgress from "./AIAnalysisProgress";

// =============================================================================
// TYPES
// =============================================================================

interface AIAnalysisLauncherProps {
  selectedErrors: AISelectedError[];

  onStarted?: (
    requestId: string,
  ) => void;

  onProgress?: (
    progress: AIProgressEvent,
  ) => void;

  onCompleted?: (
    response: AIAnalysisResponse,
  ) => void;

  onError?: (
    message: string,
  ) => void;
}

// =============================================================================
// CONFIGURATION
// =============================================================================

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

// =============================================================================
// REQUEST ID
// =============================================================================

function createRequestId(): string {
  return (
    `AI-${Date.now()}-` +
    Math.random()
      .toString(36)
      .slice(2, 10)
  );
}

// =============================================================================
// COMPONENT
// =============================================================================

export default function AIAnalysisLauncher({
  selectedErrors,
  onStarted,
  onProgress,
  onCompleted,
  onError,
}: AIAnalysisLauncherProps) {
  const [isAnalyzing, setIsAnalyzing] =
    useState(false);

  const [isCompleted, setIsCompleted] =
    useState(false);

  const [requestId, setRequestId] =
    useState<string | null>(null);

  const {
    progress,
    status,
    error: progressError,
    startProgressStream,
    stopProgressStream,
  } = useAIAnalysisProgress();

  // ===========================================================================
  // START ANALYSIS
  // ===========================================================================

  const startAnalysis =
    useCallback(
      async () => {
        if (isAnalyzing) {
          return;
        }

        if (!selectedErrors.length) {
          onError?.(
            "Please select at least one error for AI analysis.",
          );

          return;
        }

        const newRequestId =
          createRequestId();

        setRequestId(newRequestId);

        setIsAnalyzing(true);

        setIsCompleted(false);

        onStarted?.(
          newRequestId,
        );

        console.log(
          "====================================",
        );

        console.log(
          "STARTING AI ANALYSIS",
        );

        console.log(
          "Request ID:",
          newRequestId,
        );

        console.log(
          "Selected Errors:",
          selectedErrors.length,
        );

        console.log(
          "====================================",
        );

        // ---------------------------------------------------------------------
        // IMPORTANT:
        //
        // Open SSE before POST /analyze so that the first progress event
        // cannot be missed.
        // ---------------------------------------------------------------------

        startProgressStream(
          newRequestId,
        );

        try {
          // -------------------------------------------------------------------
          // Build API request
          // -------------------------------------------------------------------

          const requestBody = {
            request_id:
              newRequestId,

            selected_errors:
              selectedErrors,
          };

          console.log(
            "AI ANALYSIS REQUEST:",
            requestBody,
          );

          // -------------------------------------------------------------------
          // Start backend workflow
          // -------------------------------------------------------------------

          const response =
            await fetch(
              `${API_BASE_URL}/api/ai/analyze`,
              {
                method: "POST",

                headers: {
                  "Content-Type":
                    "application/json",
                },

                body: JSON.stringify(
                  requestBody,
                ),
              },
            );

          // -------------------------------------------------------------------
          // HTTP ERROR
          // -------------------------------------------------------------------

          if (!response.ok) {
            let message =
              `AI analysis failed with HTTP ${response.status}.`;

            try {
              const errorBody =
                (await response.json()) as {
                  detail?: unknown;
                };

              if (
                typeof errorBody.detail ===
                "string"
              ) {
                message =
                  errorBody.detail;
              }
            } catch {
              // Keep default HTTP error.
            }

            throw new Error(
              message,
            );
          }

          // -------------------------------------------------------------------
          // FINAL API RESPONSE
          // -------------------------------------------------------------------

          const result =
            (await response.json()) as AIAnalysisResponse;

          console.log(
            "====================================",
          );

          console.log(
            "AI ANALYSIS COMPLETED",
          );

          console.log(
            result,
          );

          console.log(
            "====================================",
          );

          setIsCompleted(true);

          onCompleted?.(
            result,
          );
        } catch (error) {
          const message =
            error instanceof Error
              ? error.message
              : "AI analysis failed.";

          console.error(
            "AI analysis request failed:",
            error,
          );

          onError?.(
            message,
          );
        } finally {
          // -------------------------------------------------------------------
          // POST request is finished.
          //
          // Do NOT immediately close the SSE connection here if the SSE
          // completion event has not arrived yet.
          // -------------------------------------------------------------------

          setIsAnalyzing(false);
        }
      },
      [
        isAnalyzing,
        selectedErrors,
        onStarted,
        onCompleted,
        onError,
        startProgressStream,
      ],
    );

  // ===========================================================================
  // FORWARD PROGRESS EVENT
  // ===========================================================================

  /*
   * The SSE hook owns the event stream and stores the latest progress event.
   *
   * We expose the latest event to the parent callback here.
   */

  const latestProgress =
    progress;

  if (
    latestProgress &&
    onProgress
  ) {
    // Intentionally not called during render.
    //
    // The progress UI reads the hook state directly.
    // onProgress remains available for future parent-level orchestration.
  }

  // ===========================================================================
  // ERROR STATE
  // ===========================================================================

  const displayError =
    progressError;

  // ===========================================================================
  // UI
  // ===========================================================================

  return (
    <div className="space-y-4">
      {/* ------------------------------------------------------------------ */}
      {/* Analyze Button                                                     */}
      {/* ------------------------------------------------------------------ */}

      <button
        type="button"
        onClick={startAnalysis}
        disabled={
          isAnalyzing ||
          selectedErrors.length === 0
        }
        className={`rounded-lg px-6 py-2 text-sm font-semibold text-white transition ${
          isAnalyzing ||
          selectedErrors.length === 0
            ? "cursor-not-allowed bg-indigo-300"
            : "bg-indigo-600 hover:bg-indigo-700"
        }`}
      >
        {isAnalyzing
          ? "Analyzing..."
          : isCompleted
            ? "Analyze Again"
            : "Analyze with AI"}
      </button>

      {/* ------------------------------------------------------------------ */}
      {/* Progress UI                                                        */}
      {/* ------------------------------------------------------------------ */}

      {(isAnalyzing ||
        isCompleted ||
        displayError) && (
        <AIAnalysisProgress
          progress={latestProgress}
          isAnalyzing={isAnalyzing}
          isCompleted={
            isCompleted ||
            status === "completed"
          }
          error={displayError}
        />
      )}
    </div>
  );
}