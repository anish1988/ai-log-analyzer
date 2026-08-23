"use client";

import type {
  AIAnalysisResult,
} from "@/lib/types/aiAnalysis";

// =============================================================================
// PROPS
// =============================================================================

interface AIAnalysisRootCauseEvidenceProps {
  result: AIAnalysisResult;
}

// =============================================================================
// EVIDENCE TYPE
// =============================================================================

interface EvidenceItem {
  content?: string | null;
  line_number?: number | null;
  source?: string | null;
}

// =============================================================================
// COMPONENT
// =============================================================================

export default function AIAnalysisRootCauseEvidence({
  result,
}: AIAnalysisRootCauseEvidenceProps) {
  const rootCause =
    result.root_cause?.trim() || "";

  const rootCauseEvidence =
    normalizeEvidence(
      result.root_cause_evidence,
    );

  const generalEvidence =
    normalizeEvidence(
      result.evidence,
    );

  /*
   * --------------------------------------------------------------------------
   * Prefer dedicated root_cause_evidence.
   *
   * Some RAG results currently return:
   *
   *     root_cause_evidence: []
   *
   * while the historical match still contains useful `evidence`.
   *
   * Therefore use general evidence as a fallback.
   * --------------------------------------------------------------------------
   */

  const evidence =
    rootCauseEvidence.length > 0
      ? rootCauseEvidence
      : generalEvidence;

  return (
    <section className="space-y-6">

      {/* ==================================================================== */}
      {/* HEADER                                                               */}
      {/* ==================================================================== */}

      <div className="flex items-start gap-3">

        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-50 text-rose-600">
          !
        </div>

        <div>

          <h3 className="text-lg font-semibold text-slate-800">
            Root Cause & Evidence
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            AI-generated root cause with supporting log evidence.
          </p>

        </div>

      </div>

      {/* ==================================================================== */}
      {/* ROOT CAUSE                                                           */}
      {/* ==================================================================== */}

      {rootCause ? (
        <div className="rounded-xl border border-rose-200 bg-rose-50/50 p-5">

          <div className="flex items-start gap-3">

            <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-rose-100 text-xs font-bold text-rose-700">
              RC
            </div>

            <div className="min-w-0">

              <p className="text-xs font-semibold uppercase tracking-wide text-rose-500">
                Root Cause
              </p>

              <p className="mt-2 text-sm leading-7 text-slate-700">
                {rootCause}
              </p>

            </div>

          </div>

        </div>
      ) : (
        <EmptyState
          title="Root cause not available"
          message="The analysis response did not provide a root cause."
        />
      )}

      {/* ==================================================================== */}
      {/* EVIDENCE                                                             */}
      {/* ==================================================================== */}

      <div className="rounded-xl border border-slate-200 bg-white">

        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4">

          <div>

            <h4 className="text-sm font-semibold text-slate-800">
              Supporting Evidence
            </h4>

            <p className="mt-1 text-xs text-slate-400">
              Log lines used to support the root-cause analysis.
            </p>

          </div>

          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
            {evidence.length}{" "}
            {evidence.length === 1
              ? "item"
              : "items"}
          </span>

        </div>

        {evidence.length > 0 ? (
          <div className="divide-y divide-slate-100">

            {evidence.map(
              (item, index) => (
                <EvidenceCard
                  key={`${item.line_number ?? "line"}-${index}`}
                  item={item}
                  index={index}
                />
              ),
            )}

          </div>
        ) : (
          <div className="p-5">
            <EmptyState
              title="No evidence available"
              message="No structured evidence was returned for this analysis."
            />
          </div>
        )}

      </div>

      {/* ==================================================================== */}
      {/* SOURCE INFORMATION                                                   */}
      {/* ==================================================================== */}

      {(result.source_file ||
        result.source_line_number !==
          null &&
        result.source_line_number !==
          undefined) && (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">

          <h4 className="text-sm font-semibold text-slate-800">
            Source Location
          </h4>

          <div className="mt-4 grid gap-3 sm:grid-cols-2">

            {result.source_file && (
              <InfoItem
                label="Source File"
                value={result.source_file}
                mono
              />
            )}

            {result.source_line_number !==
              null &&
              result.source_line_number !==
                undefined && (
                <InfoItem
                  label="Source Line"
                  value={String(
                    result.source_line_number,
                  )}
                  mono
                />
              )}

          </div>

        </div>
      )}

    </section>
  );
}

// =============================================================================
// EVIDENCE CARD
// =============================================================================

interface EvidenceCardProps {
  item: EvidenceItem;
  index: number;
}

function EvidenceCard({
  item,
  index,
}: EvidenceCardProps) {
  return (
    <div className="p-5">

      <div className="flex items-start gap-4">

        {/* Evidence number */}

        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-xs font-bold text-indigo-600">
          {index + 1}
        </div>

        <div className="min-w-0 flex-1">

          {/* -------------------------------------------------------------- */}
          {/* Metadata                                                        */}
          {/* -------------------------------------------------------------- */}

          <div className="flex flex-wrap items-center gap-2">

            {item.line_number !==
              null &&
              item.line_number !==
                undefined && (
                <span className="rounded-md bg-slate-100 px-2 py-1 font-mono text-[11px] font-semibold text-slate-600">
                  Line {item.line_number}
                </span>
              )}

            {item.source && (
              <span className="rounded-md bg-slate-100 px-2 py-1 text-[11px] font-medium uppercase text-slate-500">
                {item.source}
              </span>
            )}

          </div>

          {/* -------------------------------------------------------------- */}
          {/* Evidence Content                                                */}
          {/* -------------------------------------------------------------- */}

          {item.content ? (
            <div className="mt-3 overflow-x-auto rounded-lg border border-slate-200 bg-slate-950 p-4">

              <pre className="whitespace-pre-wrap break-words font-mono text-xs leading-6 text-slate-200">
                {item.content}
              </pre>

            </div>
          ) : (
            <p className="mt-3 text-sm italic text-slate-400">
              Evidence content was not provided.
            </p>
          )}

        </div>

      </div>

    </div>
  );
}

// =============================================================================
// INFO ITEM
// =============================================================================

interface InfoItemProps {
  label: string;
  value: string;
  mono?: boolean;
}

function InfoItem({
  label,
  value,
  mono = false,
}: InfoItemProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-4 py-3">

      <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p
        className={`mt-1 break-all text-sm font-semibold text-slate-700 ${
          mono ? "font-mono" : ""
        }`}
      >
        {value}
      </p>

    </div>
  );
}

// =============================================================================
// EMPTY STATE
// =============================================================================

interface EmptyStateProps {
  title: string;
  message: string;
}

function EmptyState({
  title,
  message,
}: EmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed border-slate-200 bg-slate-50 p-5">

      <p className="text-sm font-semibold text-slate-600">
        {title}
      </p>

      <p className="mt-1 text-xs leading-5 text-slate-400">
        {message}
      </p>

    </div>
  );
}

// =============================================================================
// NORMALIZE EVIDENCE
// =============================================================================

function normalizeEvidence(
  value: unknown,
): EvidenceItem[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .filter(
      (item): item is Record<
        string,
        unknown
      > =>
        typeof item === "object" &&
        item !== null,
    )
    .map((item) => ({
      content:
        typeof item.content ===
        "string"
          ? item.content
          : null,

      line_number:
        typeof item.line_number ===
        "number"
          ? item.line_number
          : null,

      source:
        typeof item.source ===
        "string"
          ? item.source
          : null,
    }))
    .filter(
      (item) =>
        Boolean(item.content) ||
        item.line_number !== null,
    );
}