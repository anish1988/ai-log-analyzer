"use client";

import { useState } from "react";

import type {
  AIAnalysisResult,
} from "@/lib/types/aiAnalysis";

interface AIAnalysisRagStatusProps {
  result: AIAnalysisResult;
}

export default function AIAnalysisRagStatus({
  result,
}: AIAnalysisRagStatusProps) {
  const [expanded, setExpanded] =
    useState(false);

  const hasRagMatch =
    result.rag_match === true;

  const similarity =
    typeof result.rag_similarity ===
    "number"
      ? result.rag_similarity
      : null;

  const similarityPercentage =
    similarity !== null
      ? Math.round(similarity * 100)
      : null;

  return (
    <section className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      {/* ================================================================ */}
      {/* Header                                                           */}
      {/* ================================================================ */}

      <button
        type="button"
        onClick={() =>
          setExpanded(
            previous => !previous,
          )
        }
        aria-expanded={expanded}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left transition hover:bg-slate-50"
      >
        <div className="flex min-w-0 items-center gap-3">
          {/* Status Icon */}

          <div
            className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
              hasRagMatch
                ? "bg-emerald-50 text-emerald-600"
                : "bg-amber-50 text-amber-600"
            }`}
          >
            {hasRagMatch
              ? "✓"
              : "↗"}
          </div>

          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-slate-800">
              RAG Status
            </h3>

            <p className="mt-0.5 truncate text-xs text-slate-500">
              {hasRagMatch
                ? "Historical knowledge matched"
                : "No historical knowledge match"}
            </p>
          </div>
        </div>

        {/* Expand Icon */}

        <span
          className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-500 transition-transform ${
            expanded
              ? "rotate-180"
              : ""
          }`}
        >
          ↓
        </span>
      </button>

      {/* ================================================================ */}
      {/* Content                                                          */}
      {/* ================================================================ */}

      {expanded && (
        <div className="border-t border-slate-200 bg-slate-50/60 p-5">
          <div className="space-y-5">
            {/* ------------------------------------------------------------ */}
            {/* Status                                                        */}
            {/* ------------------------------------------------------------ */}

            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Historical Knowledge
                </p>

                <p className="mt-1 text-sm font-semibold text-slate-700">
                  {hasRagMatch
                    ? "Match found"
                    : "No match found"}
                </p>
              </div>

              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold ${
                  hasRagMatch
                    ? "bg-emerald-50 text-emerald-700"
                    : "bg-amber-50 text-amber-700"
                }`}
              >
                {hasRagMatch
                  ? "RAG Match"
                  : "LLM Required"}
              </span>
            </div>

            {/* ------------------------------------------------------------ */}
            {/* Metrics                                                        */}
            {/* ------------------------------------------------------------ */}

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              <Metric
                label="Source"
                value={
                  result.source
                    ? result.source.toUpperCase()
                    : "—"
                }
              />

              <Metric
                label="Confidence"
                value={
                  result.confidence ||
                  "—"
                }
              />

              <Metric
                label="Similarity"
                value={
                  similarityPercentage !== null
                    ? `${similarityPercentage}%`
                    : "—"
                }
              />
            </div>

            {/* ------------------------------------------------------------ */}
            {/* Similarity Bar                                                 */}
            {/* ------------------------------------------------------------ */}

            {similarity !== null && (
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-500">
                    Knowledge similarity
                  </span>

                  <span className="text-xs font-semibold text-slate-700">
                    {similarityPercentage}%
                  </span>
                </div>

                <div className="h-2 overflow-hidden rounded-full bg-slate-200">
                  <div
                    className={`h-full rounded-full transition-all ${
                      similarityPercentage >= 80
                        ? "bg-emerald-500"
                        : similarityPercentage >= 60
                          ? "bg-indigo-500"
                          : "bg-amber-500"
                    }`}
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(
                          0,
                          similarityPercentage,
                        ),
                      )}%`,
                    }}
                  />
                </div>
              </div>
            )}

            {/* ------------------------------------------------------------ */}
            {/* Knowledge ID                                                   */}
            {/* ------------------------------------------------------------ */}

            {result.rag_knowledge_id && (
              <div>
                <p className="text-xs font-medium text-slate-400">
                  Knowledge ID
                </p>

                <div className="mt-1 rounded-lg border border-slate-200 bg-white px-3 py-2">
                  <p className="break-all font-mono text-xs text-slate-600">
                    {result.rag_knowledge_id}
                  </p>
                </div>
              </div>
            )}

            {/* ------------------------------------------------------------ */}
            {/* Explanation                                                    */}
            {/* ------------------------------------------------------------ */}

            <div className="rounded-lg border border-slate-200 bg-white p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                How this result was generated
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-600">
                {hasRagMatch
                  ? "A similar historical error was found in the knowledge base. The historical knowledge was used as part of the analysis."
                  : "No sufficiently similar historical knowledge was found. The analysis was therefore completed using the LLM."}
              </p>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

// =============================================================================
// METRIC
// =============================================================================

interface MetricProps {
  label: string;
  value: string;
}

function Metric({
  label,
  value,
}: MetricProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-4 py-3">
      <p className="text-xs font-medium text-slate-400">
        {label}
      </p>

      <p className="mt-1 truncate text-sm font-semibold text-slate-700">
        {value}
      </p>
    </div>
  );
}