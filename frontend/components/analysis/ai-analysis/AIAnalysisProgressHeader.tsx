"use client";

import type { AIProgressEvent } from "@/hooks/useAIAnalysisProgress";

interface AIAnalysisProgressHeaderProps {
  progress: AIProgressEvent | null;

  isAnalyzing: boolean;

  isCompleted?: boolean;

  error?: string | null;
}

export default function AIAnalysisProgressHeader({
  progress,
  isAnalyzing,
  isCompleted = false,
  error = null,
}: AIAnalysisProgressHeaderProps) {
  const errorNumber =
    progress?.error_index !== null &&
    progress?.error_index !== undefined
      ? progress.error_index + 1
      : null;

  const totalErrors =
    progress?.total_errors ?? null;

  // --------------------------------------------------------------------------
  // ERROR STATE
  // --------------------------------------------------------------------------

  if (error) {
    return (
      <div className="border-b border-red-100 bg-red-50 px-6 py-5">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-red-100 text-red-600">
            <span className="text-lg font-bold">
              !
            </span>
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-red-900">
                AI Analysis Failed
              </h2>

              {totalErrors !== null && (
                <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-red-700 ring-1 ring-red-200">
                  {totalErrors}{" "}
                  {totalErrors === 1
                    ? "Error"
                    : "Errors"}
                </span>
              )}
            </div>

            <p className="mt-1 text-sm text-red-700">
              {error}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // --------------------------------------------------------------------------
  // COMPLETED STATE
  // --------------------------------------------------------------------------

  if (isCompleted) {
    return (
      <div className="border-b border-emerald-100 bg-emerald-50 px-6 py-5">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
            <span className="text-lg font-bold">
              ✓
            </span>
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold text-emerald-900">
                  AI Analysis Completed
                </h2>

                <p className="mt-1 text-sm text-emerald-700">
                  All selected errors have been
                  analyzed successfully.
                </p>
              </div>

              {totalErrors !== null && (
                <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-emerald-700 ring-1 ring-emerald-200">
                  {totalErrors} / {totalErrors}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // --------------------------------------------------------------------------
  // ANALYZING STATE
  // --------------------------------------------------------------------------

  return (
    <div className="border-b border-slate-200 bg-gradient-to-r from-indigo-50 via-white to-slate-50 px-6 py-5">
      <div className="flex items-start gap-4">
        {/* ------------------------------------------------------------------ */}
        {/* Status Icon                                                        */}
        {/* ------------------------------------------------------------------ */}

        <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-indigo-600">
          <span className="text-lg">
            ✦
          </span>

          {isAnalyzing && (
            <span className="absolute inset-0 animate-ping rounded-full bg-indigo-200 opacity-40" />
          )}
        </div>

        {/* ------------------------------------------------------------------ */}
        {/* Content                                                            */}
        {/* ------------------------------------------------------------------ */}

        <div className="min-w-0 flex-1">
          {/* Title / Error Counter */}

          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-slate-800">
                AI Analysis in Progress
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Analyzing the selected errors and
                evaluating historical solutions.
              </p>
            </div>

            {/* Error Counter */}

            {errorNumber !== null &&
              totalErrors !== null && (
                <div className="shrink-0 rounded-full border border-indigo-100 bg-white px-3 py-1.5 text-xs font-semibold text-indigo-700 shadow-sm">
                  Error {errorNumber} of{" "}
                  {totalErrors}
                </div>
              )}
          </div>

          {/* ---------------------------------------------------------------- */}
          {/* Current Task                                                      */}
          {/* ---------------------------------------------------------------- */}

          {progress && (
            <div className="mt-5 rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
              <div className="flex items-start gap-3">
                <div className="mt-0.5 h-2.5 w-2.5 shrink-0 rounded-full bg-indigo-500 shadow-[0_0_0_4px_rgba(99,102,241,0.12)]" />

                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                    <span className="text-sm font-semibold text-slate-800">
                      {progress.task_name}
                    </span>

                    {progress.log_type && (
                      <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-500">
                        {progress.log_type}
                      </span>
                    )}
                  </div>

                  <p className="mt-1 text-sm leading-5 text-slate-500">
                    {progress.message}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* ---------------------------------------------------------------- */}
          {/* Status                                                            */}
          {/* ---------------------------------------------------------------- */}

          <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-slate-500">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />

              <span>
                Live analysis
              </span>
            </div>

            {progress?.status && (
              <div className="flex items-center gap-2">
                <span className="font-medium text-slate-600">
                  Status:
                </span>

                <span className="capitalize">
                  {progress.status}
                </span>
              </div>
            )}

            {progress?.progress !==
              undefined && (
              <div className="flex items-center gap-2">
                <span className="font-medium text-slate-600">
                  Current step:
                </span>

                <span>
                  {progress.progress}%
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}