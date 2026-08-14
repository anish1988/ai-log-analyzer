"use client";

import { useCallback, useEffect, useRef, useState } from "react";

// =============================================================================
// TYPES
// =============================================================================

export interface AIProgressEvent {
  request_id: string;

  error_id: string | null;

  error_index: number | null;

  total_errors: number | null;

  task_id: string;

  task_name: string;

  status: string;

  progress: number;

  message: string;

  log_type: string | null;

  metadata: Record<string, unknown>;
}

export interface AIProgressConnectionEvent {
  type: "connected";

  request_id: string;

  message: string;
}

export interface AIProgressCompletedEvent {
  type: "completed";

  request_id: string;
}

export type AIProgressStatus =
  | "idle"
  | "connecting"
  | "connected"
  | "completed"
  | "error";

interface UseAIAnalysisProgressResult {
  progress: AIProgressEvent | null;

  status: AIProgressStatus;

  error: string | null;

  isConnected: boolean;

  isCompleted: boolean;

  startProgressStream: (
    requestId: string,
  ) => void;

  stopProgressStream: () => void;
}

// =============================================================================
// CONFIGURATION
// =============================================================================

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

// =============================================================================
// HOOK
// =============================================================================

export function useAIAnalysisProgress(): UseAIAnalysisProgressResult {
  const eventSourceRef =
    useRef<EventSource | null>(null);

  const [progress, setProgress] =
    useState<AIProgressEvent | null>(null);

  const [status, setStatus] =
    useState<AIProgressStatus>("idle");

  const [error, setError] =
    useState<string | null>(null);

  // ===========================================================================
  // STOP STREAM
  // ===========================================================================

  const stopProgressStream =
    useCallback(() => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();

        eventSourceRef.current = null;
      }
    }, []);

  // ===========================================================================
  // START STREAM
  // ===========================================================================

  const startProgressStream =
    useCallback(
      (requestId: string) => {
        if (!requestId) {
          setError(
            "AI analysis request ID is required.",
          );

          setStatus("error");

          return;
        }

        // ---------------------------------------------------------------------
        // Close any previous stream
        // ---------------------------------------------------------------------

        if (eventSourceRef.current) {
          eventSourceRef.current.close();

          eventSourceRef.current = null;
        }

        // ---------------------------------------------------------------------
        // Reset state
        // ---------------------------------------------------------------------

        setProgress(null);

        setError(null);

        setStatus("connecting");

        // ---------------------------------------------------------------------
        // Build SSE URL
        // ---------------------------------------------------------------------

        const url =
          `${API_BASE_URL}/api/ai/progress/` +
          encodeURIComponent(requestId);

        console.log(
          "====================================",
        );

        console.log(
          "AI PROGRESS STREAM",
        );

        console.log(
          "====================================",
        );

        console.log(
          "Request ID:",
          requestId,
        );

        console.log(
          "SSE URL:",
          url,
        );

        console.log(
          "====================================",
        );

        // ---------------------------------------------------------------------
        // Create EventSource
        // ---------------------------------------------------------------------

        const eventSource =
          new EventSource(url);

        eventSourceRef.current =
          eventSource;

        // ---------------------------------------------------------------------
        // Connection opened
        // ---------------------------------------------------------------------

        eventSource.onopen = () => {
          console.log(
            "AI progress SSE connection opened.",
          );

          setStatus("connected");

          setError(null);
        };

        // ---------------------------------------------------------------------
        // Connected event
        // ---------------------------------------------------------------------

        eventSource.addEventListener(
          "connected",
          (event) => {
            try {
              const data =
                JSON.parse(
                  event.data,
                ) as AIProgressConnectionEvent;

              console.log(
                "AI progress stream connected:",
                data,
              );

              setStatus("connected");
            } catch {
              console.error(
                "Failed to parse SSE connected event.",
              );
            }
          },
        );

        // ---------------------------------------------------------------------
        // Progress event
        // ---------------------------------------------------------------------

        eventSource.addEventListener(
          "progress",
          (event) => {
            try {
              const data =
                JSON.parse(
                  event.data,
                ) as AIProgressEvent;

              console.log(
                "AI PROGRESS EVENT:",
                data,
              );

              setProgress(data);

              setStatus("connected");

              setError(null);
            } catch {
              console.error(
                "Failed to parse AI progress event.",
              );

              setError(
                "Received an invalid AI progress event.",
              );

              setStatus("error");
            }
          },
        );

        // ---------------------------------------------------------------------
        // Completed event
        // ---------------------------------------------------------------------

        eventSource.addEventListener(
          "completed",
          (event) => {
            try {
              const data =
                JSON.parse(
                  event.data,
                ) as AIProgressCompletedEvent;

              console.log(
                "AI ANALYSIS COMPLETED:",
                data,
              );

              setStatus("completed");

              // ---------------------------------------------------------------
              // Close stream after completion
              // ---------------------------------------------------------------

              eventSource.close();

              if (
                eventSourceRef.current ===
                eventSource
              ) {
                eventSourceRef.current =
                  null;
              }
            } catch {
              console.error(
                "Failed to parse AI completed event.",
              );

              setError(
                "Received an invalid AI completion event.",
              );

              setStatus("error");

              eventSource.close();
            }
          },
        );

        // ---------------------------------------------------------------------
        // SSE error
        // ---------------------------------------------------------------------

        eventSource.onerror = () => {
          console.error(
            "AI progress SSE connection error.",
          );

          /*
           * EventSource automatically attempts to reconnect.
           *
           * If the analysis has not completed, don't immediately
           * convert every transient network interruption into a
           * permanent error.
           */

          setError(
            "AI progress connection was interrupted.",
          );

          setStatus("error");
        };
      },
      [],
    );

  // ===========================================================================
  // CLEANUP
  // ===========================================================================

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();

        eventSourceRef.current = null;
      }
    };
  }, []);

  // ===========================================================================
  // RETURN
  // ===========================================================================

  return {
    progress,

    status,

    error,

    isConnected:
      status === "connected",

    isCompleted:
      status === "completed",

    startProgressStream,

    stopProgressStream,
  };
}

export default useAIAnalysisProgress;