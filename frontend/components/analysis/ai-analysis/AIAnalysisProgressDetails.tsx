"use client";

import { useState } from "react";

import type { AIProgressEvent } from "@/hooks/useAIAnalysisProgress";

interface AIAnalysisProgressDetailsProps {
  progress: AIProgressEvent | null;
}

export default function AIAnalysisProgressDetails({
  progress,
}: AIAnalysisProgressDetailsProps) {
  const [showTechnicalDetails, setShowTechnicalDetails] =
    useState(false);

  if (!progress) {
    return null;
  }

  const errorNumber =
    progress.error_index !== null
      ? progress.error_index + 1
      : null;

  const totalErrors =
    progress.total_errors;

  const hasMetadata =
    Object.keys(progress.metadata ?? {}).length > 0;

  return (
    <div className="space-y-4">
      {/* ------------------------------------------------------------------ */}
      {/* Current Error                                                      */}
      {/* ------------------------------------------------------------------ */}

      <div className="rounded-xl border border-slate-200 bg-white">
        <div className="px-5 py-4">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Current Error
              </p>

              <p className="mt-1 break-all text-sm font-semibold text-slate-800">
                {progress.error_id ??
                  "Processing analysis"}
              </p>
            </div>

            {errorNumber !== null &&
              totalErrors !== null && (
                <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">
                  Error {errorNumber} of{" "}
                  {totalErrors}
                </span>
              )}
          </div>

          {/* -------------------------------------------------------------- */}
          {/* Metadata                                                        */}
          {/* -------------------------------------------------------------- */}

          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <DetailItem
              label="Log Type"
              value={
                progress.log_type ??
                "—"
              }
            />

            <DetailItem
              label="Task"
              value={progress.task_id}
            />

            <DetailItem
              label="Status"
              value={progress.status}
            />
          </div>
        </div>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Technical Details                                                 */}
      {/* ------------------------------------------------------------------ */}

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
        <button
          type="button"
          onClick={() =>
            setShowTechnicalDetails(
              previous => !previous,
            )
          }
          aria-expanded={
            showTechnicalDetails
          }
          className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left transition hover:bg-slate-50"
        >
          <div>
            <p className="text-sm font-semibold text-slate-700">
              Technical Details
            </p>

            <p className="mt-1 text-xs text-slate-400">
              Request and workflow information
            </p>
          </div>

          <span
            className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-500 transition-transform ${
              showTechnicalDetails
                ? "rotate-180"
                : ""
            }`}
          >
            ↓
          </span>
        </button>

        {showTechnicalDetails && (
          <div className="border-t border-slate-200 bg-slate-50/70 px-5 py-4">
            <div className="space-y-4">
              {/* ---------------------------------------------------------- */}
              {/* Request ID                                                  */}
              {/* ---------------------------------------------------------- */}

              <DetailItem
                label="Request ID"
                value={progress.request_id}
                monospace
              />

              {/* ---------------------------------------------------------- */}
              {/* Error ID                                                    */}
              {/* ---------------------------------------------------------- */}

              {progress.error_id && (
                <DetailItem
                  label="Error ID"
                  value={progress.error_id}
                  monospace
                />
              )}

              {/* ---------------------------------------------------------- */}
              {/* Task ID                                                     */}
              {/* ---------------------------------------------------------- */}

              <DetailItem
                label="Task ID"
                value={progress.task_id}
                monospace
              />

              {/* ---------------------------------------------------------- */}
              {/* Message                                                     */}
              {/* ---------------------------------------------------------- */}

              <div>
                <p className="mb-1 text-xs font-medium text-slate-400">
                  Message
                </p>

                <div className="rounded-lg border border-slate-200 bg-white px-3 py-2">
                  <p className="break-words text-xs leading-5 text-slate-600">
                    {progress.message ||
                      "—"}
                  </p>
                </div>
              </div>

              {/* ---------------------------------------------------------- */}
              {/* Metadata                                                    */}
              {/* ---------------------------------------------------------- */}

              {hasMetadata && (
                <div>
                  <p className="mb-1 text-xs font-medium text-slate-400">
                    Metadata
                  </p>

                  <pre className="max-h-64 overflow-auto rounded-lg border border-slate-200 bg-slate-900 p-4 text-[11px] leading-5 text-slate-200">
                    {JSON.stringify(
                      progress.metadata,
                      null,
                      2,
                    )}
                  </pre>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// SMALL DETAIL COMPONENT
// =============================================================================

interface DetailItemProps {
  label: string;

  value: string;

  monospace?: boolean;
}

function DetailItem({
  label,
  value,
  monospace = false,
}: DetailItemProps) {
  return (
    <div className="min-w-0">
      <p className="text-xs font-medium text-slate-400">
        {label}
      </p>

      <div className="mt-1 rounded-lg bg-slate-50 px-3 py-2">
        <p
          className={`truncate text-xs text-slate-600 ${
            monospace
              ? "font-mono"
              : ""
          }`}
          title={value}
        >
          {value || "—"}
        </p>
      </div>
    </div>
  );
}