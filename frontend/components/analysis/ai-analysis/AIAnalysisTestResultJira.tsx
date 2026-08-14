"use client";

import { useState } from "react";

import type {
  AIAnalysisResult,
} from "@/lib/types/aiAnalysis";

interface AIAnalysisTestResultJiraProps {
  result: AIAnalysisResult;
}

export default function AIAnalysisTestResultJira({
  result,
}: AIAnalysisTestResultJiraProps) {
  return (
    <section className="space-y-4">
      {/* ================================================================ */}
      {/* Test Result                                                      */}
      {/* ================================================================ */}

      <TestResultCard result={result} />

      {/* ================================================================ */}
      {/* Jira Description                                                 */}
      {/* ================================================================ */}

      <JiraDescriptionCard
        description={
          result.jira_description
        }
      />
    </section>
  );
}

// =============================================================================
// TEST RESULT
// =============================================================================

interface TestResultCardProps {
  result: AIAnalysisResult;
}

function TestResultCard({
  result,
}: TestResultCardProps) {
  const [expanded, setExpanded] =
    useState(false);

  const testResult =
    result.test_result;

  if (!testResult) {
    return (
      <section className="rounded-xl border border-dashed border-slate-200 bg-white p-5">
        <p className="text-sm font-semibold text-slate-700">
          Test Result
        </p>

        <p className="mt-2 text-sm text-slate-400">
          No test result was returned by the AI analysis.
        </p>
      </section>
    );
  }

  const steps =
    testResult.test_steps ?? [];

  const status =
    testResult.status ?? "unknown";

  const statusIsRecommended =
    status.toLowerCase() ===
    "recommended";

  return (
    <section className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      {/* ------------------------------------------------------------------ */}
      {/* Header                                                             */}
      {/* ------------------------------------------------------------------ */}

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
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-cyan-50 text-cyan-600">
            ✓
          </div>

          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-slate-800">
              Test Result
            </h3>

            <p className="mt-1 text-xs text-slate-500">
              Recommended validation steps and expected outcome.
            </p>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <span
            className={`hidden rounded-full px-2.5 py-1 text-[11px] font-semibold sm:inline-flex ${
              statusIsRecommended
                ? "bg-emerald-50 text-emerald-700"
                : "bg-slate-100 text-slate-600"
            }`}
          >
            {status}
          </span>

          <span
            className={`flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-slate-500 transition-transform ${
              expanded
                ? "rotate-180"
                : ""
            }`}
          >
            ↓
          </span>
        </div>
      </button>

      {/* ------------------------------------------------------------------ */}
      {/* Content                                                            */}
      {/* ------------------------------------------------------------------ */}

      {expanded && (
        <div className="border-t border-slate-200 bg-slate-50/50 p-5">
          <div className="space-y-5">
            {/* ------------------------------------------------------------ */}
            {/* Status                                                        */}
            {/* ------------------------------------------------------------ */}

            <div className="flex items-center justify-between gap-3">
              <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Status
              </span>

              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold ${
                  statusIsRecommended
                    ? "bg-emerald-50 text-emerald-700"
                    : "bg-slate-100 text-slate-600"
                }`}
              >
                {status}
              </span>
            </div>

            {/* ------------------------------------------------------------ */}
            {/* Test Steps                                                    */}
            {/* ------------------------------------------------------------ */}

            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
                Validation Steps
              </p>

              {steps.length === 0 ? (
                <div className="rounded-xl border border-dashed border-slate-200 bg-white p-4">
                  <p className="text-sm text-slate-400">
                    No test steps were provided.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {steps.map(
                    (step, index) => (
                      <div
                        key={`${index}-${step}`}
                        className="flex gap-3 rounded-xl border border-slate-200 bg-white p-4"
                      >
                        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-cyan-50 text-xs font-semibold text-cyan-700">
                          {index + 1}
                        </span>

                        <p className="min-w-0 break-words text-sm leading-6 text-slate-600">
                          {step}
                        </p>
                      </div>
                    ),
                  )}
                </div>
              )}
            </div>

            {/* ------------------------------------------------------------ */}
            {/* Expected Result                                               */}
            {/* ------------------------------------------------------------ */}

            {testResult.expected_result && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Expected Result
                </p>

                <div className="rounded-xl border border-emerald-100 bg-emerald-50/50 p-4">
                  <p className="break-words text-sm leading-6 text-slate-700">
                    {
                      testResult.expected_result
                    }
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}

// =============================================================================
// JIRA DESCRIPTION
// =============================================================================

interface JiraDescriptionCardProps {
  description?: string | null;
}

function JiraDescriptionCard({
  description,
}: JiraDescriptionCardProps) {
  const [expanded, setExpanded] =
    useState(false);

  const hasDescription =
    Boolean(description?.trim());

  return (
    <section className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      {/* ------------------------------------------------------------------ */}
      {/* Header                                                             */}
      {/* ------------------------------------------------------------------ */}

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
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-violet-50 text-violet-600">
            J
          </div>

          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-slate-800">
              Jira Description
            </h3>

            <p className="mt-1 text-xs text-slate-500">
              AI-generated issue description ready for Jira.
            </p>
          </div>
        </div>

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

      {/* ------------------------------------------------------------------ */}
      {/* Content                                                            */}
      {/* ------------------------------------------------------------------ */}

      {expanded && (
        <div className="border-t border-slate-200 bg-slate-50/50 p-5">
          {!hasDescription ? (
            <div className="rounded-xl border border-dashed border-slate-200 bg-white p-5 text-center">
              <p className="text-sm text-slate-400">
                No Jira description was generated.
              </p>
            </div>
          ) : (
            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <div className="max-h-[500px] overflow-auto">
                <pre className="whitespace-pre-wrap break-words font-sans text-sm leading-6 text-slate-700">
                  {description}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}