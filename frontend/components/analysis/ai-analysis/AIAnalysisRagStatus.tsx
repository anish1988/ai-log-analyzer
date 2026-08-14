"use client";

import type {
  AIAnalysisResultResponse,
} from "@/lib/types/aiAnalysis";

// =============================================================================
// PROPS
// =============================================================================

interface AIAnalysisRagStatusProps {
  result: AIAnalysisResultResponse;
}

// =============================================================================
// COMPONENT
// =============================================================================

export default function AIAnalysisRagStatus({
  result,
}: AIAnalysisRagStatusProps) {
  const similarity =
    typeof result.rag_similarity === "number"
      ? result.rag_similarity
      : null;

  const similarityPercentage =
    similarity !== null
      ? Math.round(similarity * 100)
      : null;

  const hasMatch =
    result.rag_match === true;

  const confidence =
    result.confidence || "none";

  /*
   * --------------------------------------------------------------------------
   * IMPORTANT
   *
   * A RAG match does NOT automatically mean that the historical solution
   * was reused.
   *
   * The backend can find a historical match and still send the error through
   * the LLM analysis branch.
   * --------------------------------------------------------------------------
   */

  const ragStatus = getRagStatus({
    hasMatch,
    confidence,
    similarity,
  });

  return (
    <section className="space-y-6">

      {/* ==================================================================== */}
      {/* HEADER                                                               */}
      {/* ==================================================================== */}

      <div className="flex flex-wrap items-start justify-between gap-4">

        <div>

          <div className="flex items-center gap-3">

            <div
              className={`flex h-10 w-10 items-center justify-center rounded-xl ${
                hasMatch
                  ? "bg-emerald-50 text-emerald-600"
                  : "bg-slate-100 text-slate-500"
              }`}
            >
              {hasMatch ? "✓" : "?"}
            </div>

            <div>

              <h3 className="text-lg font-semibold text-slate-800">
                RAG / Historical Knowledge
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                Historical knowledge retrieval and decision status.
              </p>

            </div>

          </div>

        </div>

        {/* Status */}

        <span
          className={`rounded-full px-3 py-1.5 text-xs font-semibold ${ragStatus.badgeClass}`}
        >
          {ragStatus.label}
        </span>

      </div>

      {/* ==================================================================== */}
      {/* STATUS SUMMARY                                                       */}
      {/* ==================================================================== */}

      <div
        className={`rounded-xl border p-5 ${ragStatus.containerClass}`}
      >

        <div className="flex items-start gap-3">

          <div
            className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${ragStatus.iconClass}`}
          >
            {ragStatus.icon}
          </div>

          <div>

            <h4
              className={`text-sm font-semibold ${ragStatus.titleClass}`}
            >
              {ragStatus.title}
            </h4>

            <p
              className={`mt-1 text-sm leading-6 ${ragStatus.textClass}`}
            >
              {ragStatus.description}
            </p>

          </div>

        </div>

      </div>

      {/* ==================================================================== */}
      {/* RAG METRICS                                                          */}
      {/* ==================================================================== */}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

        <MetricCard
          label="Match Found"
          value={hasMatch ? "Yes" : "No"}
          valueClass={
            hasMatch
              ? "text-emerald-600"
              : "text-slate-600"
          }
        />

        <MetricCard
          label="Similarity"
          value={
            similarityPercentage !== null
              ? `${similarityPercentage}%`
              : "N/A"
          }
        />

        <MetricCard
          label="Confidence"
          value={
            confidence === "none"
              ? "N/A"
              : formatConfidence(
                  confidence,
                )
          }
        />

        <MetricCard
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

      {/* ==================================================================== */}
      {/* SIMILARITY BAR                                                       */}
      {/* ==================================================================== */}

      {similarityPercentage !== null && (
        <div className="rounded-xl border border-slate-200 bg-white p-5">

          <div className="flex items-center justify-between">

            <div>

              <h4 className="text-sm font-semibold text-slate-800">
                RAG Similarity
              </h4>

              <p className="mt-1 text-xs text-slate-400">
                Similarity score returned by historical knowledge retrieval.
              </p>

            </div>

            <span className="text-sm font-bold text-slate-700">
              {similarityPercentage}%
            </span>

          </div>

          <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">

            <div
              className={`h-full rounded-full transition-all ${
                similarityPercentage >= 92
                  ? "bg-emerald-500"
                  : similarityPercentage >= 80
                    ? "bg-amber-500"
                    : "bg-slate-400"
              }`}
              style={{
                width: `${Math.min(
                  Math.max(
                    similarityPercentage,
                    0,
                  ),
                  100,
                )}%`,
              }}
            />

          </div>

          <div className="mt-2 flex justify-between text-[10px] text-slate-400">

            <span>0%</span>

            <span>Review: 80%</span>

            <span>Reuse: 92%</span>

            <span>100%</span>

          </div>

        </div>
      )}

      {/* ==================================================================== */}
      {/* KNOWLEDGE INFORMATION                                                */}
      {/* ==================================================================== */}

      {hasMatch &&
        result.rag_knowledge_id !==
          null &&
        result.rag_knowledge_id !==
          undefined && (
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">

            <div className="flex flex-wrap items-center justify-between gap-3">

              <div>

                <h4 className="text-sm font-semibold text-slate-800">
                  Historical Knowledge Match
                </h4>

                <p className="mt-1 text-xs text-slate-400">
                  A historical knowledge record was identified for this error.
                </p>

              </div>

              <span className="rounded-lg bg-white px-3 py-1.5 font-mono text-xs font-semibold text-slate-600 ring-1 ring-slate-200">
                Knowledge #{result.rag_knowledge_id}
              </span>

            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-2">

              <InfoRow
                label="Knowledge ID"
                value={String(
                  result.rag_knowledge_id,
                )}
              />

              <InfoRow
                label="Similarity"
                value={
                  similarityPercentage !==
                  null
                    ? `${similarityPercentage}%`
                    : "N/A"
                }
              />

              <InfoRow
                label="Confidence"
                value={formatConfidence(
                  confidence,
                )}
              />

              <InfoRow
                label="Source"
                value={
                  result.source ||
                  "Unknown"
                }
              />

            </div>

          </div>
        )}

      {/* ==================================================================== */}
      {/* NO MATCH                                                             */}
      {/* ==================================================================== */}

      {!hasMatch && (
        <div className="rounded-xl border border-slate-200 bg-white p-5">

          <div className="flex items-start gap-3">

            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-500">
              i
            </div>

            <div>

              <h4 className="text-sm font-semibold text-slate-800">
                No Historical Solution Found
              </h4>

              <p className="mt-1 text-sm leading-6 text-slate-500">
                No suitable historical RAG match was found for this error.
                The analysis therefore requires the AI/LLM analysis path.
              </p>

            </div>

          </div>

        </div>
      )}

    </section>
  );
}

// =============================================================================
// RAG STATUS
// =============================================================================

interface RagStatusInput {
  hasMatch: boolean;
  confidence: string;
  similarity: number | null;
}

function getRagStatus({
  hasMatch,
  confidence,
  similarity,
}: RagStatusInput) {
  if (!hasMatch) {
    return {
      label: "No Match",
      title: "No historical match found",
      description:
        "The RAG retrieval did not find a suitable historical solution. The error requires AI/LLM analysis.",
      icon: "i",
      iconClass:
        "bg-slate-100 text-slate-500",
      badgeClass:
        "bg-slate-100 text-slate-600",
      containerClass:
        "border-slate-200 bg-slate-50",
      titleClass:
        "text-slate-700",
      textClass:
        "text-slate-500",
    };
  }

  /*
   * High confidence / high similarity.
   *
   * The backend uses the reuse threshold of 0.92.
   */

  if (
    confidence === "high" &&
    similarity !== null &&
    similarity >= 0.92
  ) {
    return {
      label: "Historical Solution Reused",
      title:
        "Trusted historical solution available",
      description:
        "A high-confidence historical match was found and is suitable for reuse.",
      icon: "✓",
      iconClass:
        "bg-emerald-100 text-emerald-700",
      badgeClass:
        "bg-emerald-50 text-emerald-700",
      containerClass:
        "border-emerald-200 bg-emerald-50/50",
      titleClass:
        "text-emerald-800",
      textClass:
        "text-emerald-700",
    };
  }

  /*
   * Match exists but the backend did not consider it safe enough to reuse.
   */

  return {
    label: "LLM Validation Required",
    title:
      "Historical match found but not reused",
    description:
      "A historical match was found, but it was not considered sufficiently reliable for direct reuse. The error continues through the LLM analysis path.",
    icon: "AI",
    iconClass:
      "bg-amber-100 text-amber-700",
    badgeClass:
      "bg-amber-50 text-amber-700",
    containerClass:
      "border-amber-200 bg-amber-50/50",
    titleClass:
      "text-amber-800",
    textClass:
      "text-amber-700",
  };
}

// =============================================================================
// METRIC CARD
// =============================================================================

interface MetricCardProps {
  label: string;
  value: string;
  valueClass?: string;
}

function MetricCard({
  label,
  value,
  valueClass = "text-slate-800",
}: MetricCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">

      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p
        className={`mt-2 text-lg font-bold ${valueClass}`}
      >
        {value}
      </p>

    </div>
  );
}

// =============================================================================
// INFO ROW
// =============================================================================

interface InfoRowProps {
  label: string;
  value: string;
}

function InfoRow({
  label,
  value,
}: InfoRowProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-4 py-3">

      <p className="text-[10px] font-medium uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p className="mt-1 break-words text-sm font-semibold text-slate-700">
        {value}
      </p>

    </div>
  );
}

// =============================================================================
// CONFIDENCE FORMATTER
// =============================================================================

function formatConfidence(
  confidence: string,
): string {
  if (!confidence) {
    return "N/A";
  }

  return (
    confidence.charAt(0).toUpperCase() +
    confidence.slice(1)
  );
}