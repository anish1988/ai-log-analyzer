"use client";

import { useMemo, useState } from "react";

import type { AIProgressEvent } from "@/hooks/useAIAnalysisProgress";

interface AIAnalysisProgressProps {
  progress: AIProgressEvent | null;
  isAnalyzing: boolean;
  isCompleted: boolean;
  error: string | null;
  onClose?: () => void;
}

export default function AIAnalysisProgress({
  progress,
  isAnalyzing,
  isCompleted,
  error,
  onClose,
}: AIAnalysisProgressProps) {
  const [showDetails, setShowDetails] =
    useState(false);

  /*
   * --------------------------------------------------------------------------
   * Progress information
   * --------------------------------------------------------------------------
   */

  const totalErrors =
    progress?.total_errors ?? 0;

  const currentErrorIndex =
    progress?.error_index ?? 0;

  const currentErrorNumber =
    totalErrors > 0
      ? currentErrorIndex + 1
      : 0;

  const currentProgress =
    progress?.progress ?? 0;

  /*
   * Backend progress is per-error.
   *
   * Example:
   *
   * Error 1 / 3 -> 80%
   * Error 2 / 3 -> 80%
   * Error 3 / 3 -> 80%
   *
   * We convert that into an overall progress value.
   */

  const overallProgress =
    useMemo(() => {
      if (isCompleted) {
        return 100;
      }

      if (totalErrors <= 0) {
        return currentProgress;
      }

      const completedErrors =
        currentErrorIndex;

      const calculated =
        (
          (completedErrors +
            currentProgress / 100) /
          totalErrors
        ) * 100;

      return Math.min(
        100,
        Math.max(
          0,
          Math.round(calculated),
        ),
      );
    }, [
      isCompleted,
      totalErrors,
      currentErrorIndex,
      currentProgress,
    ]);

  /*
   * --------------------------------------------------------------------------
   * Current task
   * --------------------------------------------------------------------------
   */

  const taskName =
    progress?.task_name ??
    (isCompleted
      ? "AI analysis completed"
      : "Preparing AI analysis");

  const taskMessage =
    progress?.message ??
    (isCompleted
      ? "All selected errors have been analyzed."
      : "Starting AI analysis.");

  /*
   * --------------------------------------------------------------------------
   * Status
   * --------------------------------------------------------------------------
   */

  const statusText = error
    ? "Analysis failed"
    : isCompleted
      ? "Analysis completed"
      : "Analysis in progress";

  /*
   * --------------------------------------------------------------------------
   * Modal
   * --------------------------------------------------------------------------
   */

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/50 px-4 py-6 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="ai-analysis-title"
    >
      {/* ------------------------------------------------------------------ */}
      {/* Modal                                                              */}
      {/* ------------------------------------------------------------------ */}

      <div className="w-full max-w-2xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">

        {/* ---------------------------------------------------------------- */}
        {/* Header                                                           */}
        {/* ---------------------------------------------------------------- */}

        <div className="border-b border-slate-200 bg-gradient-to-r from-indigo-50 via-white to-purple-50 px-6 py-5">

          <div className="flex items-start justify-between gap-4">

            <div className="flex items-start gap-4">

              {/* Icon */}

              <div
                className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ${
                  error
                    ? "bg-red-100 text-red-600"
                    : isCompleted
                      ? "bg-emerald-100 text-emerald-600"
                      : "bg-indigo-100 text-indigo-600"
                }`}
              >
                {error ? (
                  <span className="text-xl">
                    !
                  </span>
                ) : isCompleted ? (
                  <span className="text-xl">
                    ✓
                  </span>
                ) : (
                  <span className="text-lg">
                    ✦
                  </span>
                )}
              </div>

              <div>

                <h2
                  id="ai-analysis-title"
                  className="text-lg font-semibold text-slate-900"
                >
                  {error
                    ? "AI Analysis Failed"
                    : isCompleted
                      ? "AI Analysis Complete"
                      : "AI Analysis in Progress"}
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  {error
                    ? "The AI analysis could not be completed."
                    : isCompleted
                      ? `Successfully analyzed ${totalErrors || "all"} selected error${
                          totalErrors === 1
                            ? ""
                            : "s"
                        }.`
                      : "Analyzing the selected errors and evaluating historical solutions."}
                </p>

              </div>

            </div>

            {/* Error counter */}

            {!error &&
              totalErrors > 0 && (
                <div className="shrink-0 rounded-full border border-indigo-100 bg-white px-3 py-1.5 text-xs font-semibold text-indigo-600 shadow-sm">
                  {isCompleted
                    ? `${totalErrors} of ${totalErrors}`
                    : `Error ${currentErrorNumber} of ${totalErrors}`}
                </div>
              )}

          </div>

        </div>

        {/* ---------------------------------------------------------------- */}
        {/* Body                                                             */}
        {/* ---------------------------------------------------------------- */}

        <div className="px-6 py-6">

          {/* Error */}

          {error ? (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4">

              <div className="flex gap-3">

                <div className="mt-0.5 text-red-600">
                  ⚠
                </div>

                <div className="min-w-0">

                  <p className="text-sm font-semibold text-red-800">
                    Unable to complete AI analysis
                  </p>

                  <p className="mt-1 break-words text-sm text-red-700">
                    {error}
                  </p>

                </div>

              </div>

            </div>
          ) : (
            <>
              {/* ---------------------------------------------------------- */}
              {/* Current Task                                                */}
              {/* ---------------------------------------------------------- */}

              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">

                <div className="flex items-start gap-3">

                  <div
                    className={`mt-1 h-3 w-3 shrink-0 rounded-full ${
                      isCompleted
                        ? "bg-emerald-500"
                        : "bg-indigo-500"
                    } ${
                      isAnalyzing
                        ? "animate-pulse"
                        : ""
                    }`}
                  />

                  <div className="min-w-0 flex-1">

                    <div className="flex flex-wrap items-center gap-2">

                      <h3 className="text-sm font-semibold text-slate-800">
                        {taskName}
                      </h3>

                      {progress?.log_type && (
                        <span className="rounded-full bg-white px-2 py-0.5 text-[11px] font-medium text-slate-500 shadow-sm">
                          {progress.log_type}
                        </span>
                      )}

                    </div>

                    <p className="mt-1 text-sm text-slate-500">
                      {taskMessage}
                    </p>

                  </div>

                </div>

                {/* Live status */}

                <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-500">

                  <span className="flex items-center gap-1.5">

                    <span
                      className={`h-2 w-2 rounded-full ${
                        isCompleted
                          ? "bg-emerald-500"
                          : "bg-emerald-500 animate-pulse"
                      }`}
                    />

                    {isCompleted
                      ? "Completed"
                      : "Live analysis"}

                  </span>

                  <span>
                    Status:{" "}
                    <strong className="font-semibold text-slate-700">
                      {statusText}
                    </strong>
                  </span>

                  {!isCompleted &&
                    progress && (
                      <span>
                        Current step:{" "}
                        <strong className="font-semibold text-slate-700">
                          {currentProgress}%
                        </strong>
                      </span>
                    )}

                </div>

              </div>

              {/* ---------------------------------------------------------- */}
              {/* Overall Progress                                             */}
              {/* ---------------------------------------------------------- */}

              <div className="mt-6">

                <div className="flex items-end justify-between gap-4">

                  <div>

                    <p className="text-sm font-semibold text-slate-800">
                      Overall Analysis Progress
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      {isCompleted
                        ? "All selected errors have been processed."
                        : totalErrors > 0
                          ? `Processing error ${currentErrorNumber} of ${totalErrors}`
                          : "Preparing analysis..."}
                    </p>

                  </div>

                  <span className="text-xl font-bold text-indigo-600">
                    {overallProgress}%
                  </span>

                </div>

                {/* Main progress bar */}

                <div className="mt-3 h-3 overflow-hidden rounded-full bg-slate-100">

                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      isCompleted
                        ? "bg-emerald-500"
                        : "bg-gradient-to-r from-indigo-500 to-purple-500"
                    }`}
                    style={{
                      width: `${overallProgress}%`,
                    }}
                  />

                </div>

                {/* Error progress indicators */}

                {totalErrors > 0 && (
                  <div className="mt-3 flex gap-2">

                    {Array.from({
                      length: totalErrors,
                    }).map(
                      (_, index) => {

                        const completed =
                          isCompleted ||
                          index <
                            currentErrorIndex;

                        const current =
                          !isCompleted &&
                          index ===
                            currentErrorIndex;

                        return (
                          <div
                            key={index}
                            className={`h-1.5 flex-1 rounded-full transition-all ${
                              completed
                                ? "bg-indigo-500"
                                : current
                                  ? "bg-indigo-300"
                                  : "bg-slate-100"
                            }`}
                          />
                        );
                      },
                    )}

                  </div>
                )}

              </div>

              {/* ---------------------------------------------------------- */}
              {/* Details Toggle                                              */}
              {/* ---------------------------------------------------------- */}

              <div className="mt-6 border-t border-slate-200 pt-4">

                <button
                  type="button"
                  onClick={() =>
                    setShowDetails(
                      previous =>
                        !previous,
                    )
                  }
                  className="flex w-full items-center justify-between rounded-lg px-2 py-2 text-left text-sm font-medium text-slate-600 transition hover:bg-slate-50"
                >

                  <span>
                    {showDetails
                      ? "Hide analysis details"
                      : "View analysis details"}
                  </span>

                  <span className="text-slate-400">
                    {showDetails
                      ? "↑"
                      : "↓"}
                  </span>

                </button>

                {showDetails && (
                  <div className="mt-3 max-h-56 overflow-y-auto rounded-xl border border-slate-200 bg-slate-50 p-4">

                    <div className="space-y-3 text-sm">

                      <div className="flex items-center justify-between gap-4">
                        <span className="text-slate-500">
                          Current task
                        </span>

                        <span className="text-right font-medium text-slate-700">
                          {taskName}
                        </span>
                      </div>

                      <div className="flex items-center justify-between gap-4">
                        <span className="text-slate-500">
                          Error
                        </span>

                        <span className="font-medium text-slate-700">
                          {totalErrors > 0
                            ? `${currentErrorNumber} / ${totalErrors}`
                            : "-"}
                        </span>
                      </div>

                      <div className="flex items-center justify-between gap-4">
                        <span className="text-slate-500">
                          Current progress
                        </span>

                        <span className="font-medium text-slate-700">
                          {currentProgress}%
                        </span>
                      </div>

                      {progress?.error_id && (
                        <div className="flex items-center justify-between gap-4">
                          <span className="text-slate-500">
                            Error ID
                          </span>

                          <span className="break-all text-right font-mono text-xs text-slate-700">
                            {progress.error_id}
                          </span>
                        </div>
                      )}

                    </div>

                  </div>
                )}

              </div>
            </>
          )}

        </div>

        {/* ---------------------------------------------------------------- */}
        {/* Footer                                                           */}
        {/* ---------------------------------------------------------------- */}

        <div className="flex items-center justify-between border-t border-slate-200 bg-slate-50 px-6 py-4">

          <div className="text-xs text-slate-400">
            {isCompleted
              ? "Analysis is ready to review."
              : error
                ? "Please close this window and try again."
                : "Please wait while AI processes the selected errors."}
          </div>

          <div className="flex items-center gap-3">

            {error && (
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
              >
                Close
              </button>
            )}

            {isCompleted && (
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700"
              >
                View Analysis Results →
              </button>
            )}

          </div>

        </div>

      </div>
    </div>
  );
}