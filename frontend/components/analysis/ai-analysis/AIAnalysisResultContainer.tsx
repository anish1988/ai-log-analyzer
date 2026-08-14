"use client";

import type {
  AIAnalysisResponse,
  AIAnalysisResult,
} from "@/lib/types/aiAnalysis";

import AIAnalysisRagStatus from "./AIAnalysisRagStatus";
import AIAnalysisRootCauseEvidence from "./AIAnalysisRootCauseEvidence";
import AIAnalysisSolutionOptimization from "./AIAnalysisSolutionOptimization";
import AIAnalysisTestResultJira from "./AIAnalysisTestResultJira";

interface AIAnalysisResultContainerProps {
  response: AIAnalysisResponse;
}

export default function AIAnalysisResultContainer({
  response,
}: AIAnalysisResultContainerProps) {
  const results =
    response.final_results ?? [];

  return (
    <section className="space-y-6">
      {/* ================================================================ */}
      {/* Result Header                                                    */}
      {/* ================================================================ */}

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                ✦
              </div>

              <div>
                <h2 className="text-xl font-bold text-slate-800">
                  AI Analysis Results
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Analysis completed successfully.
                </p>
              </div>
            </div>
          </div>

          <span className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Completed
          </span>
        </div>

        {/* ============================================================ */}
        {/* Summary Stats                                                 */}
        {/* ============================================================ */}

        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          <SummaryItem
            label="Errors Analyzed"
            value={String(
              response.total_errors ?? 0,
            )}
          />

          <SummaryItem
            label="Completed"
            value={String(
              response.completed_errors ?? 0,
            )}
          />

          <SummaryItem
            label="Progress"
            value={`${response.progress ?? 100}%`}
          />
        </div>
      </div>

      {/* ================================================================ */}
      {/* Empty Result                                                     */}
      {/* ================================================================ */}

      {results.length === 0 && (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center shadow-sm">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-400">
            AI
          </div>

          <h3 className="mt-4 text-base font-semibold text-slate-700">
            No analysis results available
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            The AI workflow completed, but no individual
            analysis results were returned.
          </p>
        </div>
      )}

      {/* ================================================================ */}
      {/* Individual Results                                               */}
      {/* ================================================================ */}

      <div className="space-y-6">
        {results.map(
          (result, index) => (
            <AIAnalysisResultCard
              key={
                result.error_id ??
                `result-${index}`
              }
              result={result}
              index={index}
            />
          ),
        )}
      </div>
    </section>
  );
}

// =============================================================================
// RESULT CARD
// =============================================================================

interface AIAnalysisResultCardProps {
  result: AIAnalysisResult;
  index: number;
}

function AIAnalysisResultCard({
  result,
  index,
}: AIAnalysisResultCardProps) {
  return (
    <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      {/* ------------------------------------------------------------------ */}
      {/* Error Header                                                       */}
      {/* ------------------------------------------------------------------ */}

      <div className="border-b border-slate-200 px-6 py-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Error {index + 1}
            </p>

            <h3 className="mt-1 break-words text-lg font-semibold text-slate-800">
              {result.title ||
                result.error_id ||
                "AI Analysis Result"}
            </h3>

            {result.error_id && (
              <p className="mt-2 break-all font-mono text-xs text-slate-400">
                {result.error_id}
              </p>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {result.tier && (
              <span className="rounded-full bg-indigo-50 px-2.5 py-1 text-[11px] font-semibold capitalize text-indigo-700">
                {result.tier}
              </span>
            )}

            {result.source && (
              <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-medium uppercase text-slate-600">
                {result.source}
              </span>
            )}

            {result.confidence &&
              result.confidence !== "none" && (
                <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-[11px] font-semibold capitalize text-emerald-700">
                  {result.confidence}
                </span>
              )}
          </div>
        </div>

        {/* -------------------------------------------------------------- */}
        {/* Error Summary                                                   */}
        {/* -------------------------------------------------------------- */}

        {result.error_summary && (
          <div className="mt-5 rounded-xl bg-slate-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
              Summary
            </p>

            <p className="mt-2 break-words text-sm leading-6 text-slate-700">
              {result.error_summary}
            </p>
          </div>
        )}
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Analysis Details                                                   */}
      {/* ------------------------------------------------------------------ */}

      <div className="space-y-4 p-6">
        {/* RAG */}

        <AIAnalysisRagStatus
          result={result}
        />

        {/* Root Cause + Evidence */}

        <AIAnalysisRootCauseEvidence
          result={result}
        />

        {/* Solution + Optimization */}

        <AIAnalysisSolutionOptimization
          result={result}
        />

        {/* Test Result + Jira */}

        <AIAnalysisTestResultJira
          result={result}
        />
      </div>
    </article>
  );
}

// =============================================================================
// SUMMARY ITEM
// =============================================================================

interface SummaryItemProps {
  label: string;
  value: string;
}

function SummaryItem({
  label,
  value,
}: SummaryItemProps) {
  return (
    <div className="rounded-xl border border-slate-100 bg-slate-50 px-4 py-3">
      <p className="text-xs font-medium text-slate-400">
        {label}
      </p>

      <p className="mt-1 text-lg font-bold text-slate-800">
        {value}
      </p>
    </div>
  );
}