"use client";

import type {
  AIAnalysisResult,
} from "@/lib/types/aiAnalysis";

// =============================================================================
// PROPS
// =============================================================================

interface AIAnalysisSolutionOptimizationProps {
  result: AIAnalysisResult;
}

// =============================================================================
// COMPONENT
// =============================================================================

export default function AIAnalysisSolutionOptimization({
  result,
}: AIAnalysisSolutionOptimizationProps) {
  const solution =
    result.solution?.trim() || "";

  const optimization =
    result.optimization?.trim() || "";

  const hasSolution =
    solution.length > 0;

  const hasOptimization =
    optimization.length > 0;

  return (
    <section className="space-y-6">

      {/* ==================================================================== */}
      {/* HEADER                                                               */}
      {/* ==================================================================== */}

      <div className="flex items-start gap-3">

        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
          →
        </div>

        <div>

          <h3 className="text-lg font-semibold text-slate-800">
            Solution & Optimization
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Recommended resolution and improvements to prevent the issue
            from recurring.
          </p>

        </div>

      </div>

      {/* ==================================================================== */}
      {/* SOLUTION + OPTIMIZATION                                              */}
      {/* ==================================================================== */}

      <div className="grid gap-5 lg:grid-cols-2">

        {/* ================================================================== */}
        {/* SOLUTION                                                           */}
        {/* ================================================================== */}

        <SolutionCard
          title="Recommended Solution"
          description="Actions recommended to resolve the current issue."
          value={solution}
          available={hasSolution}
          variant="solution"
        />

        {/* ================================================================== */}
        {/* OPTIMIZATION                                                        */}
        {/* ================================================================== */}

        <SolutionCard
          title="Optimization"
          description="Improvements recommended to reduce the chance of recurrence."
          value={optimization}
          available={hasOptimization}
          variant="optimization"
        />

      </div>

      {/* ==================================================================== */}
      {/* RESOLUTION SOURCE                                                    */}
      {/* ==================================================================== */}

      <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">

        <div className="flex flex-wrap items-center justify-between gap-3">

          <div>

            <h4 className="text-sm font-semibold text-slate-800">
              Resolution Source
            </h4>

            <p className="mt-1 text-xs text-slate-400">
              Indicates where the recommended resolution originated.
            </p>

          </div>

          <SourceBadge
            source={result.source}
          />

        </div>

        {/* RAG information */}

        {result.rag_match && (
          <div className="mt-4 grid gap-3 sm:grid-cols-2">

            <InfoItem
              label="Historical Match"
              value="Found"
            />

            <InfoItem
              label="Knowledge ID"
              value={
                result.rag_knowledge_id !==
                  null &&
                result.rag_knowledge_id !==
                  undefined
                  ? String(
                      result.rag_knowledge_id,
                    )
                  : "N/A"
              }
            />

          </div>
        )}

      </div>

      {/* ==================================================================== */}
      {/* ACTION SUMMARY                                                       */}
      {/* ==================================================================== */}

      {(hasSolution ||
        hasOptimization) && (
        <div className="rounded-xl border border-slate-200 bg-white p-5">

          <h4 className="text-sm font-semibold text-slate-800">
            Recommended Action Plan
          </h4>

          <div className="mt-4 space-y-3">

            {hasSolution && (
              <ActionItem
                number={1}
                title="Resolve the current issue"
                description={
                  "Apply the recommended solution to address the identified root cause."
                }
              />
            )}

            {hasOptimization && (
              <ActionItem
                number={
                  hasSolution ? 2 : 1
                }
                title="Prevent recurrence"
                description={
                  "Apply the optimization recommendations to improve long-term reliability."
                }
              />
            )}

          </div>

        </div>
      )}

      {/* ==================================================================== */}
      {/* EMPTY STATE                                                          */}
      {/* ==================================================================== */}

      {!hasSolution &&
        !hasOptimization && (
          <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6">

            <div className="flex items-start gap-3">

              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-200 text-slate-500">
                i
              </div>

              <div>

                <h4 className="text-sm font-semibold text-slate-700">
                  Solution information not available
                </h4>

                <p className="mt-1 text-sm leading-6 text-slate-500">
                  The analysis completed, but no solution or optimization
                  recommendation was returned.
                </p>

              </div>

            </div>

          </div>
        )}

    </section>
  );
}

// =============================================================================
// SOLUTION CARD
// =============================================================================

interface SolutionCardProps {
  title: string;
  description: string;
  value: string;
  available: boolean;
  variant:
    | "solution"
    | "optimization";
}

function SolutionCard({
  title,
  description,
  value,
  available,
  variant,
}: SolutionCardProps) {
  const isSolution =
    variant === "solution";

  return (
    <div
      className={`rounded-xl border p-5 ${
        isSolution
          ? "border-emerald-200 bg-emerald-50/40"
          : "border-indigo-200 bg-indigo-50/40"
      }`}
    >

      {/* Header */}

      <div className="flex items-start gap-3">

        <div
          className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
            isSolution
              ? "bg-emerald-100 text-emerald-700"
              : "bg-indigo-100 text-indigo-700"
          }`}
        >
          {isSolution ? "✓" : "↗"}
        </div>

        <div className="min-w-0">

          <h4 className="text-sm font-semibold text-slate-800">
            {title}
          </h4>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            {description}
          </p>

        </div>

      </div>

      {/* Content */}

      {available ? (
        <div className="mt-5 rounded-lg border border-white/80 bg-white p-4 shadow-sm">

          <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">
            {value}
          </p>

        </div>
      ) : (
        <div className="mt-5 rounded-lg border border-dashed border-slate-200 bg-white/70 p-4">

          <p className="text-sm italic text-slate-400">
            No recommendation provided.
          </p>

        </div>
      )}

    </div>
  );
}

// =============================================================================
// SOURCE BADGE
// =============================================================================

interface SourceBadgeProps {
  source?: string | null;
}

function SourceBadge({
  source,
}: SourceBadgeProps) {
  const normalizedSource =
    source?.trim().toLowerCase() ||
    "unknown";

  const isRag =
    normalizedSource === "rag";

  const isLlm =
    normalizedSource === "llm";

  const label = isRag
    ? "Historical Knowledge"
    : isLlm
      ? "AI / LLM Analysis"
      : formatSource(
          normalizedSource,
        );

  const className = isRag
    ? "bg-emerald-50 text-emerald-700"
    : isLlm
      ? "bg-indigo-50 text-indigo-700"
      : "bg-slate-100 text-slate-600";

  return (
    <span
      className={`rounded-full px-3 py-1.5 text-xs font-semibold ${className}`}
    >
      {label}
    </span>
  );
}

// =============================================================================
// INFO ITEM
// =============================================================================

interface InfoItemProps {
  label: string;
  value: string;
}

function InfoItem({
  label,
  value,
}: InfoItemProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-4 py-3">

      <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p className="mt-1 text-sm font-semibold text-slate-700">
        {value}
      </p>

    </div>
  );
}

// =============================================================================
// ACTION ITEM
// =============================================================================

interface ActionItemProps {
  number: number;
  title: string;
  description: string;
}

function ActionItem({
  number,
  title,
  description,
}: ActionItemProps) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-slate-100 bg-slate-50 p-4">

      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-white text-xs font-bold text-indigo-600 ring-1 ring-slate-200">
        {number}
      </div>

      <div>

        <h5 className="text-sm font-semibold text-slate-700">
          {title}
        </h5>

        <p className="mt-1 text-xs leading-5 text-slate-500">
          {description}
        </p>

      </div>

    </div>
  );
}

// =============================================================================
// SOURCE FORMATTER
// =============================================================================

function formatSource(
  source: string,
): string {
  if (!source) {
    return "Unknown";
  }

  return (
    source.charAt(0).toUpperCase() +
    source.slice(1)
  );
}