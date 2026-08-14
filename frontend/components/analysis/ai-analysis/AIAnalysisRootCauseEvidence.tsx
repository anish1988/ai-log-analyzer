"use client";

import { useState } from "react";

import type {
  AIAnalysisResult,
} from "@/lib/types/aiAnalysis";

interface AIAnalysisRootCauseEvidenceProps {
  result: AIAnalysisResult;
}

export default function AIAnalysisRootCauseEvidence({
  result,
}: AIAnalysisRootCauseEvidenceProps) {
  const [showEvidence, setShowEvidence] =
    useState(true);

  const evidence =
    result.root_cause_evidence ?? [];

  return (
    <section className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      {/* ================================================================ */}
      {/* Root Cause Header                                                */}
      {/* ================================================================ */}

      <div className="border-b border-slate-200 px-5 py-5">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-rose-50 text-rose-600">
            !
          </div>

          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-slate-800">
              Root Cause
            </h3>

            <p className="mt-1 text-xs text-slate-500">
              AI-identified cause based on the available evidence.
            </p>
          </div>
        </div>

        {/* ============================================================ */}
        {/* Root Cause                                                     */}
        {/* ============================================================ */}

        {result.root_cause ? (
          <div className="mt-5 rounded-xl border border-rose-100 bg-rose-50/40 p-4">
            <p className="text-sm leading-6 text-slate-700">
              {result.root_cause}
            </p>
          </div>
        ) : (
          <div className="mt-5 rounded-xl border border-dashed border-slate-200 bg-slate-50 p-4">
            <p className="text-sm text-slate-400">
              Root cause information is not available.
            </p>
          </div>
        )}
      </div>

      {/* ================================================================ */}
      {/* Evidence Header                                                  */}
      {/* ================================================================ */}

      <button
        type="button"
        onClick={() =>
          setShowEvidence(
            previous => !previous,
          )
        }
        aria-expanded={showEvidence}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left transition hover:bg-slate-50"
      >
        <div>
          <p className="text-sm font-semibold text-slate-700">
            Root Cause Evidence
          </p>

          <p className="mt-1 text-xs text-slate-400">
            {evidence.length > 0
              ? `${evidence.length} evidence ${
                  evidence.length === 1
                    ? "item"
                    : "items"
                }`
              : "No evidence items available"}
          </p>
        </div>

        <span
          className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-500 transition-transform ${
            showEvidence
              ? "rotate-180"
              : ""
          }`}
        >
          ↓
        </span>
      </button>

      {/* ================================================================ */}
      {/* Evidence List                                                    */}
      {/* ================================================================ */}

      {showEvidence && (
        <div className="border-t border-slate-200 bg-slate-50/50 p-5">
          {evidence.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-200 bg-white p-5 text-center">
              <p className="text-sm text-slate-400">
                No supporting evidence was returned by the AI analysis.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {evidence.map(
                (item, index) => (
                  <EvidenceItem
                    key={`${item.line_number ?? "line"}-${index}`}
                    index={index}
                    lineNumber={
                      item.line_number
                    }
                    content={
                      item.content
                    }
                    explanation={
                      item.explanation
                    }
                  />
                ),
              )}
            </div>
          )}
        </div>
      )}
    </section>
  );
}

// =============================================================================
// EVIDENCE ITEM
// =============================================================================

interface EvidenceItemProps {
  index: number;
  lineNumber?: number | null;
  content?: string | null;
  explanation?: string | null;
}

function EvidenceItem({
  index,
  lineNumber,
  content,
  explanation,
}: EvidenceItemProps) {
  const [expanded, setExpanded] =
    useState(false);

  const hasExplanation =
    Boolean(explanation);

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      {/* ------------------------------------------------------------------ */}
      {/* Evidence Header                                                   */}
      {/* ------------------------------------------------------------------ */}

      <button
        type="button"
        onClick={() =>
          setExpanded(
            previous => !previous,
          )
        }
        className="flex w-full items-center gap-3 px-4 py-3 text-left transition hover:bg-slate-50"
        aria-expanded={expanded}
      >
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-xs font-semibold text-indigo-600">
          {index + 1}
        </span>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold text-slate-700">
              Evidence {index + 1}
            </span>

            {lineNumber !== null &&
              lineNumber !== undefined && (
                <span className="rounded-full bg-slate-100 px-2 py-0.5 font-mono text-[10px] text-slate-500">
                  Line {lineNumber}
                </span>
              )}
          </div>

          {!expanded && (
            <p className="mt-1 line-clamp-2 break-words font-mono text-xs leading-5 text-slate-500">
              {content ||
                "No evidence content available."}
            </p>
          )}
        </div>

        <span
          className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-400 transition-transform ${
            expanded
              ? "rotate-180"
              : ""
          }`}
        >
          ↓
        </span>
      </button>

      {/* ------------------------------------------------------------------ */}
      {/* Expanded Evidence                                                 */}
      {/* ------------------------------------------------------------------ */}

      {expanded && (
        <div className="border-t border-slate-200 bg-slate-50/60 p-4">
          <div className="space-y-4">
            {/* ------------------------------------------------------------ */}
            {/* Raw Evidence                                                 */}
            {/* ------------------------------------------------------------ */}

            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                Evidence
              </p>

              <div className="max-h-64 overflow-auto rounded-lg border border-slate-200 bg-slate-900 p-4">
                <pre className="whitespace-pre-wrap break-words font-mono text-xs leading-5 text-slate-200">
                  {content ||
                    "No evidence content available."}
                </pre>
              </div>
            </div>

            {/* ------------------------------------------------------------ */}
            {/* Explanation                                                   */}
            {/* ------------------------------------------------------------ */}

            {hasExplanation && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Why this supports the root cause
                </p>

                <div className="rounded-lg border border-indigo-100 bg-indigo-50/50 p-4">
                  <p className="text-sm leading-6 text-slate-600">
                    {explanation}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}