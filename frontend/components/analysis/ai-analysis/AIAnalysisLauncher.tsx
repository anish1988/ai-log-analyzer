"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

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
  // ---------------------------------------------------------------------------
  // Analysis lifecycle
  // ---------------------------------------------------------------------------

  const [analysisStarted, setAnalysisStarted] =
    useState(false);

  const [pendingResponse, setPendingResponse] =
    useState<AIAnalysisResponse | null>(null);

  const [requestError, setRequestError] =
    useState<string | null>(null);

  // ---------------------------------------------------------------------------
  // Prevent duplicate completion callback
  // ---------------------------------------------------------------------------

  const completionNotifiedRef =
    useRef(false);

  // ---------------------------------------------------------------------------
  // SSE progress
  // ---------------------------------------------------------------------------

  const {
    progress,
    status,
    error: progressError,
    startProgressStream,
    stopProgressStream,
  } = useAIAnalysisProgress();

  // =============================================================================
  // DERIVED STATE
  // =============================================================================

  /*
   * The SSE hook is the source of truth for workflow completion.
   *
   * The backend sends:
   *
   * event: completed
   *
   * The hook then changes:
   *
   * status = "completed"
   *
   * We additionally require the POST response to be available before
   * considering the entire analysis ready.
   */

  const isCompleted =
    status === "completed" &&
    pendingResponse !== null;

  /*
   * Analysis is still running while:
   *
   * 1. analysis was started
   * 2. SSE has not completed
   * 3. there is no fatal request error
   */

  const isAnalyzing =
    analysisStarted &&
    !isCompleted &&
    !requestError;

  /*
   * Progress error and API request error are displayed through the
   * same progress modal.
   */

  const displayError =
    progressError ??
    requestError;

  // =============================================================================
  // START ANALYSIS
  // =============================================================================

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

        // -----------------------------------------------------------------------
        // Create request ID
        // -----------------------------------------------------------------------

        const newRequestId =
          createRequestId();

        // -----------------------------------------------------------------------
        // Reset previous analysis state
        // -----------------------------------------------------------------------

        completionNotifiedRef.current =
          false;

        setAnalysisStarted(true);

        setPendingResponse(null);

        setRequestError(null);

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

        // -----------------------------------------------------------------------
        // Start SSE BEFORE POST
        //
        // This prevents the first progress event from being missed.
        // -----------------------------------------------------------------------

        startProgressStream(
          newRequestId,
        );

        try {
          // ---------------------------------------------------------------------
          // Request body
          // ---------------------------------------------------------------------

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

          // ---------------------------------------------------------------------
          // Start backend analysis
          // ---------------------------------------------------------------------

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

          // ---------------------------------------------------------------------
          // HTTP ERROR
          // ---------------------------------------------------------------------

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

          // ---------------------------------------------------------------------
          // API response
          //
          // IMPORTANT:
          //
          // Do NOT close the popup here.
          //
          // The POST response only means the HTTP request has completed.
          // The SSE stream still needs to send the final "completed" event.
          // ---------------------------------------------------------------------

          const result =
            (await response.json()) as AIAnalysisResponse;

          console.log(
            "====================================",
          );

          console.log(
            "AI ANALYSIS API RESPONSE RECEIVED",
          );

          console.log(
            result,
          );

          console.log(
            "====================================",
          );

          setPendingResponse(
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

          // ---------------------------------------------------------------------
          // Stop SSE because the actual API request failed.
          // ---------------------------------------------------------------------

          stopProgressStream();

          setRequestError(
            message,
          );

          setAnalysisStarted(
            false,
          );

          setPendingResponse(
            null,
          );

          onError?.(
            message,
          );
        }
      },
      [
        isAnalyzing,
        selectedErrors,
        onStarted,
        onError,
        startProgressStream,
        stopProgressStream,
      ],
    );

  // =============================================================================
  // FORWARD PROGRESS
  // =============================================================================

  useEffect(() => {
    if (!progress) {
      return;
    }

    onProgress?.(
      progress,
    );
  }, [
    progress,
    onProgress,
  ]);

  // =============================================================================
  // SSE COMPLETION
  // =============================================================================

  /*
   * This effect does NOT update React state.
   *
   * It only notifies the parent that the complete AI response is ready.
   *
   * This avoids the React set-state-in-effect lint error.
   */

  useEffect(() => {
    if (
      status !== "completed" ||
      !pendingResponse
    ) {
      return;
    }

    if (
      completionNotifiedRef.current
    ) {
      return;
    }

    completionNotifiedRef.current =
      true;

    console.log(
      "====================================",
    );

    console.log(
      "AI ANALYSIS WORKFLOW COMPLETED",
    );

    console.log(
      "All selected errors processed.",
    );

    console.log(
      "Total errors:",
      pendingResponse.total_errors,
    );

    console.log(
      "Progress:",
      pendingResponse.progress,
    );

    console.log(
      "====================================",
    );

    onCompleted?.(
      pendingResponse,
    );
  }, [
    status,
    pendingResponse,
    onCompleted,
  ]);

  // =============================================================================
  // CLOSE POPUP
  // =============================================================================

  const handleClose =
    useCallback(() => {
      /*
       * Do not allow the popup to close while analysis is still running.
       *
       * An error is allowed to close because the workflow has already failed.
       */

      if (
        !isCompleted &&
        !displayError
      ) {
        return;
      }

      console.log(
        "====================================",
      );

      console.log(
        "AI ANALYSIS POPUP CLOSED",
      );

      console.log(
        "====================================",
      );

      stopProgressStream();

      setAnalysisStarted(
        false,
      );

      setPendingResponse(
        null,
      );

      setRequestError(
        null,
      );
    }, [
      isCompleted,
      displayError,
      stopProgressStream,
    ]);

  // =============================================================================
  // UI
  // =============================================================================

  return (
    <div className="space-y-4">

      {/* ===================================================================== */}
      {/* Analyze Button                                                        */}
      {/* ===================================================================== */}

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

      {/* ===================================================================== */}
      {/* AI Progress Modal                                                     */}
      {/* ===================================================================== */}

      {(isAnalyzing ||
        isCompleted ||
        displayError) && (
        <AIAnalysisProgress
          progress={
            progress
          }
          isAnalyzing={
            isAnalyzing
          }
          isCompleted={
            isCompleted
          }
          error={
            displayError
          }
          onClose={
            handleClose
          }
        />
      )}

    </div>
  );
}