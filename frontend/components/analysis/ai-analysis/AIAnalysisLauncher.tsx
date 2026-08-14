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

  /**
   * Called when a new AI analysis request starts.
   */
  onStarted?: (
    requestId: string,
  ) => void;

  /**
   * Called whenever a new SSE progress event is received.
   *
   * The progress UI is handled internally by this component.
   */
  onProgress?: (
    progress: AIProgressEvent,
  ) => void;

  /**
   * Called when the backend returns the final AI analysis response.
   *
   * IMPORTANT:
   * This does NOT close the progress modal.
   *
   * The user must explicitly click
   * "View Analysis Results".
   */
  onCompleted?: (
    response: AIAnalysisResponse,
  ) => void;

  /**
   * Called only after the user clicks
   * "View Analysis Results".
   *
   * Parent should use this callback to move
   * from Step 2 -> Step 3.
   */
  onClosed?: (
    response: AIAnalysisResponse,
  ) => void;

  /**
   * Called when AI analysis fails.
   */
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
  onClosed,
  onError,
}: AIAnalysisLauncherProps) {
  // ===========================================================================
  // LOCAL STATE
  // ===========================================================================

  const [
    isAnalyzing,
    setIsAnalyzing,
  ] = useState(false);

  const [
    isCompleted,
    setIsCompleted,
  ] = useState(false);

  /**
   * Final response returned by:
   *
   * POST /api/ai/analyze
   */
  const [
    completedResponse,
    setCompletedResponse,
  ] = useState<AIAnalysisResponse | null>(
    null,
  );

  /**
   * Controls the progress modal.
   */
  const [
    isProgressModalOpen,
    setIsProgressModalOpen,
  ] = useState(false);

  // ===========================================================================
  // AI PROGRESS SSE
  // ===========================================================================

  const {
    progress,
    status,
    error: progressError,
    startProgressStream,
    stopProgressStream,
  } = useAIAnalysisProgress();

  // ===========================================================================
  // ANALYSIS COMPLETION STATE
  // ===========================================================================

  /**
   * The completed UI state is based on the two pieces of information
   * that belong to this component:
   *
   * 1. Backend returned the final AI response.
   * 2. Launcher marked the analysis as completed.
   *
   * We intentionally do NOT depend on the SSE status here.
   *
   * The SSE is responsible for displaying progress.
   * The final API response is responsible for providing the
   * actual analysis result.
   *
   * This avoids a situation where the button is visible but
   * a second condition prevents the click from doing anything.
   */
  const analysisComplete =
    isCompleted &&
    completedResponse !== null;

  // ===========================================================================
  // START ANALYSIS
  // ===========================================================================

  const startAnalysis =
    useCallback(
      async () => {
        // -----------------------------------------------------------------------
        // Prevent duplicate requests
        // -----------------------------------------------------------------------

        if (isAnalyzing) {
          return;
        }

        // -----------------------------------------------------------------------
        // Validate selection
        // -----------------------------------------------------------------------

        if (
          selectedErrors.length ===
          0
        ) {
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

        setIsAnalyzing(true);

        setIsCompleted(false);

        setCompletedResponse(
          null,
        );

        // -----------------------------------------------------------------------
        // Open progress modal
        // -----------------------------------------------------------------------

        setIsProgressModalOpen(
          true,
        );

        // -----------------------------------------------------------------------
        // Notify parent
        // -----------------------------------------------------------------------

        onStarted?.(
          newRequestId,
        );

        // -----------------------------------------------------------------------
        // Debug logging
        // -----------------------------------------------------------------------

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
        // IMPORTANT:
        //
        // Start SSE BEFORE POST.
        // -----------------------------------------------------------------------

        startProgressStream(
          newRequestId,
        );

        try {
          // =====================================================================
          // BUILD REQUEST
          // =====================================================================

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

          // =====================================================================
          // START BACKEND AI ANALYSIS
          // =====================================================================

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

          // =====================================================================
          // HTTP ERROR
          // =====================================================================

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
              // Keep default HTTP message.
            }

            throw new Error(
              message,
            );
          }

          // =====================================================================
          // FINAL API RESPONSE
          // =====================================================================

          const result =
            (await response.json()) as AIAnalysisResponse;

          console.log(
            "====================================",
          );

          console.log(
            "AI ANALYSIS API COMPLETED",
          );

          console.log(
            result,
          );

          console.log(
            "====================================",
          );

          // =====================================================================
          // STORE FINAL RESPONSE
          // =====================================================================

          /**
           * IMPORTANT:
           *
           * Do NOT close the modal here.
           *
           * Do NOT move to Step 3 here.
           *
           * The completed response is stored first.
           *
           * The user must explicitly click:
           *
           * "View Analysis Results"
           */

          setCompletedResponse(
            result,
          );

          setIsCompleted(true);

          // ---------------------------------------------------------------------
          // Notify parent
          // ---------------------------------------------------------------------

          onCompleted?.(
            result,
          );
        } catch (error) {
          // =====================================================================
          // ERROR
          // =====================================================================

          const message =
            error instanceof Error
              ? error.message
              : "AI analysis failed.";

          console.error(
            "AI analysis request failed:",
            error,
          );

          // ---------------------------------------------------------------------
          // Stop SSE
          // ---------------------------------------------------------------------

          stopProgressStream();

          // ---------------------------------------------------------------------
          // Reset state
          // ---------------------------------------------------------------------

          setIsAnalyzing(false);

          setIsCompleted(false);

          setCompletedResponse(
            null,
          );

          // ---------------------------------------------------------------------
          // Notify parent
          // ---------------------------------------------------------------------

          onError?.(
            message,
          );
        } finally {
          // =====================================================================
          // POST REQUEST FINISHED
          // =====================================================================

          /**
           * Do NOT close the modal here.
           *
           * The modal stays open until the user
           * clicks "View Analysis Results".
           */

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
        stopProgressStream,
      ],
    );

  // ===========================================================================
  // PROGRESS
  // ===========================================================================

  const latestProgress =
    progress;

  /**
   * Keep this callback available for future parent-level
   * progress orchestration.
   *
   * We intentionally do not call onProgress during render.
   */
  void onProgress;

  // ===========================================================================
  // ERROR
  // ===========================================================================

  const displayError =
    progressError;

  // ===========================================================================
  // VIEW AI RESULTS
  // ===========================================================================

  const handleViewResults =
    useCallback(() => {
      // -------------------------------------------------------------------------
      // Safety check
      // -------------------------------------------------------------------------

      if (!completedResponse) {
        console.warn(
          "View Analysis Results clicked, but completed response is missing.",
        );

        return;
      }

      console.log(
        "====================================",
      );

      console.log(
        "VIEW AI ANALYSIS RESULTS",
      );

      console.log(
        "Request ID:",
        completedResponse.request_id,
      );

      console.log(
        "Progress:",
        progress?.progress,
      );

      console.log(
        "Status:",
        status,
      );

      console.log(
        "====================================",
      );

      // -------------------------------------------------------------------------
      // Close modal
      // -------------------------------------------------------------------------

      setIsProgressModalOpen(
        false,
      );

      // -------------------------------------------------------------------------
      // Stop SSE defensively.
      // -------------------------------------------------------------------------

      stopProgressStream();

      // -------------------------------------------------------------------------
      // Tell parent to move to Step 3.
      //
      // IMPORTANT:
      // No new LLM request is made here.
      //
      // We pass the response that is already stored in state.
      // -------------------------------------------------------------------------

      onClosed?.(
        completedResponse,
      );
    }, [
      completedResponse,
      progress?.progress,
      status,
      stopProgressStream,
      onClosed,
    ]);

  // ===========================================================================
  // CLOSE ERROR MODAL
  // ===========================================================================

  const handleCloseError =
    useCallback(() => {
      stopProgressStream();

      setIsProgressModalOpen(
        false,
      );

      setIsAnalyzing(false);
    }, [
      stopProgressStream,
    ]);

  // ===========================================================================
  // UI
  // ===========================================================================

  return (
    <>
      {/* ====================================================================== */}
      {/* ANALYZE BUTTON                                                         */}
      {/* ====================================================================== */}

      <button
        type="button"
        onClick={
          startAnalysis
        }
        disabled={
          isAnalyzing ||
          selectedErrors.length ===
            0
        }
        className={`rounded-lg px-6 py-2 text-sm font-semibold text-white transition ${
          isAnalyzing ||
          selectedErrors.length ===
            0
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

      {/* ====================================================================== */}
      {/* AI ANALYSIS PROGRESS MODAL                                             */}
      {/* ====================================================================== */}

      {isProgressModalOpen && (
        <div
          className="
            fixed
            inset-0
            z-[9999]
            flex
            items-center
            justify-center
            bg-slate-950/50
            p-4
            backdrop-blur-sm
          "
          role="presentation"
        >
          <div
            className="
              relative
              z-10
              max-h-[90vh]
              w-full
              max-w-3xl
              overflow-y-auto
              rounded-2xl
              bg-white
              shadow-2xl
            "
            role="dialog"
            aria-modal="true"
            aria-labelledby="ai-analysis-progress-title"
          >
            {/* ================================================================ */}
            {/* HEADER                                                            */}
            {/* ================================================================ */}

            <div
              className="
                flex
                items-center
                justify-between
                gap-4
                border-b
                border-slate-200
                px-6
                py-4
              "
            >
              <div>
                <h2
                  id="ai-analysis-progress-title"
                  className="
                    text-lg
                    font-semibold
                    text-slate-800
                  "
                >
                  AI Analysis
                </h2>

                <p
                  className="
                    mt-1
                    text-sm
                    text-slate-500
                  "
                >
                  Analyzing the selected
                  errors
                </p>
              </div>

              {/* ============================================================ */}
              {/* STATUS                                                         */}
              {/* ============================================================ */}

              {analysisComplete && (
                <span
                  className="
                    rounded-full
                    bg-emerald-50
                    px-3
                    py-1
                    text-xs
                    font-semibold
                    text-emerald-700
                  "
                >
                  Completed
                </span>
              )}

              {isAnalyzing && (
                <span
                  className="
                    rounded-full
                    bg-indigo-50
                    px-3
                    py-1
                    text-xs
                    font-semibold
                    text-indigo-700
                  "
                >
                  Analyzing
                </span>
              )}

              {displayError && (
                <span
                  className="
                    rounded-full
                    bg-rose-50
                    px-3
                    py-1
                    text-xs
                    font-semibold
                    text-rose-700
                  "
                >
                  Failed
                </span>
              )}
            </div>

            {/* ================================================================ */}
            {/* PROGRESS                                                          */}
            {/* ================================================================ */}

            <div className="p-6">
              <AIAnalysisProgress
                progress={
                  latestProgress
                }
                isAnalyzing={
                  isAnalyzing
                }
                isCompleted={
                  analysisComplete
                }
                error={
                  displayError
                }
                onViewResults={
                    handleViewResults
                }
              />
            </div>

            {/* ================================================================ */}
            {/* SUCCESS FOOTER                                                   */}
            {/* ================================================================ */}

            {analysisComplete && (
              <div
                className="
                  relative
                  z-20
                  flex
                  items-center
                  justify-between
                  gap-4
                  border-t
                  border-slate-200
                  bg-white
                  px-6
                  py-4
                "
              >
                <div>
                  <p
                    className="
                      text-sm
                      font-semibold
                      text-slate-800
                    "
                  >
                    AI analysis completed
                  </p>

                  <p
                    className="
                      mt-1
                      text-xs
                      text-slate-500
                    "
                  >
                    All selected errors
                    have been analyzed.
                  </p>
                </div>

                {/* ============================================================ */}
                {/* VIEW RESULTS BUTTON                                           */}
                {/* ============================================================ */}

           {/*      <button
                  type="button"
                  onClick={
                    handleViewResults
                  }
                  disabled={
                    !completedResponse
                  }
                  className="
                    relative
                    z-30
                    pointer-events-auto
                    cursor-pointer
                    rounded-lg
                    bg-indigo-600
                    px-6
                    py-2.5
                    text-sm
                    font-semibold
                    text-white
                    shadow-sm
                    transition
                    hover:bg-indigo-700
                    active:bg-indigo-800
                    focus:outline-none
                    focus:ring-2
                    focus:ring-indigo-500
                    focus:ring-offset-2
                    disabled:cursor-not-allowed
                    disabled:bg-indigo-300
                  "
                >
                  View Analysis Results →
                </button>    */}
              </div>
            )}

            {/* ================================================================ */}
            {/* ERROR FOOTER                                                     */}
            {/* ================================================================ */}

            {displayError &&
              !isAnalyzing && (
                <div
                  className="
                    relative
                    z-20
                    flex
                    items-center
                    justify-end
                    border-t
                    border-slate-200
                    bg-white
                    px-6
                    py-4
                  "
                >
                  <button
                    type="button"
                    onClick={
                      handleCloseError
                    }
                    className="
                      rounded-lg
                      border
                      border-slate-300
                      px-6
                      py-2.5
                      text-sm
                      font-semibold
                      text-slate-700
                      transition
                      hover:bg-slate-100
                    "
                  >
                    Close
                  </button>
                </div>
              )}
          </div>
        </div>
      )}
    </>
  );
}