"use client";

import type { AIProgressEvent } from "@/hooks/useAIAnalysisProgress";

interface AIAnalysisProgressBarProps {
  progress: AIProgressEvent | null;
}

export default function AIAnalysisProgressBar({
  progress,
}: AIAnalysisProgressBarProps) {
  // --------------------------------------------------------------------------
  // No progress yet
  // --------------------------------------------------------------------------

  if (!progress) {
    return (
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-slate-600">
            Preparing analysis
          </span>

          <span className="text-sm font-semibold text-indigo-600">
            0%
          </span>
        </div>

        <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
          <div className="h-full w-0 rounded-full bg-indigo-500" />
        </div>
      </div>
    );
  }

  const totalErrors =
    progress.total_errors ?? 1;

  const errorIndex =
    progress.error_index ?? 0;

  const currentProgress =
    Math.max(
      0,
      Math.min(
        progress.progress,
        100,
      ),
    );

  // --------------------------------------------------------------------------
  // Calculate overall progress
  //
  // Example:
  //
  // Error 1 / 3 at 100%
  //     => 33.3%
  //
  // Error 2 / 3 at 50%
  //     => 50%
  //
  // Error 3 / 3 at 100%
  //     => 100%
  // --------------------------------------------------------------------------

  const overallProgress =
    totalErrors > 0
      ? Math.round(
          Math.min(
            100,
            (
              (errorIndex +
                currentProgress / 100) /
              totalErrors
            ) *
              100,
          ),
        )
      : currentProgress;

  // --------------------------------------------------------------------------
  // Current error number
  // --------------------------------------------------------------------------

  const currentErrorNumber =
    Math.min(
      errorIndex + 1,
      totalErrors,
    );

  return (
    <div className="space-y-4">
      {/* ------------------------------------------------------------------ */}
      {/* Progress Header                                                   */}
      {/* ------------------------------------------------------------------ */}

      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-slate-800">
            Overall Analysis Progress
          </p>

          <p className="mt-1 text-xs text-slate-500">
            Processing error{" "}
            {currentErrorNumber} of{" "}
            {totalErrors}
          </p>
        </div>

        <div className="text-right">
          <span className="text-2xl font-bold tracking-tight text-indigo-600">
            {overallProgress}%
          </span>
        </div>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Progress Track                                                    */}
      {/* ------------------------------------------------------------------ */}

      <div
        className="relative h-3 overflow-hidden rounded-full bg-slate-100"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={overallProgress}
        aria-label="Overall AI analysis progress"
      >
        {/* Background Track */}

        <div className="absolute inset-0 rounded-full bg-slate-100" />

        {/* Progress Fill */}

        <div
          className="relative h-full rounded-full bg-gradient-to-r from-indigo-500 via-violet-500 to-indigo-600 transition-all duration-500 ease-out"
          style={{
            width: `${overallProgress}%`,
          }}
        >
          {/* Moving Highlight */}

          {overallProgress > 0 &&
            overallProgress < 100 && (
              <div className="absolute inset-y-0 right-0 w-16 bg-gradient-to-r from-transparent to-white/30" />
            )}
        </div>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Progress Metadata                                                  */}
      {/* ------------------------------------------------------------------ */}

      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
        <span>
          Current task progress:{" "}
          <span className="font-semibold text-slate-700">
            {currentProgress}%
          </span>
        </span>

        <span>
          {currentErrorNumber} /{" "}
          {totalErrors} errors
        </span>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Error Progress Indicators                                         */}
      {/* ------------------------------------------------------------------ */}

      {totalErrors > 1 && (
        <div className="flex items-center gap-1.5">
          {Array.from(
            {
              length: totalErrors,
            },
            (_, index) => {
              const completed =
                index < errorIndex;

              const current =
                index === errorIndex;

              return (
                <div
                  key={index}
                  className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${
                    completed
                      ? "bg-indigo-500"
                      : current
                        ? "bg-indigo-200"
                        : "bg-slate-100"
                  }`}
                  title={`Error ${index + 1}`}
                />
              );
            },
          )}
        </div>
      )}
    </div>
  );
}