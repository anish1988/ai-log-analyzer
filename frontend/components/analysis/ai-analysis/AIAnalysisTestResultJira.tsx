"use client";

import { useMemo, useState } from "react";

import type {
  AIAnalysisResult,
} from "@/lib/types/aiAnalysis";

// =============================================================================
// TYPES
// =============================================================================

interface AIAnalysisTestResultJiraProps {
  result: AIAnalysisResult;
}

interface TestResult {
  status?: string;
  test_case?: string;
  expected_result?: string;
  verification_steps?: string[];
  test_steps?: string[];
  [key: string]: unknown;
}

// =============================================================================
// COMPONENT
// =============================================================================

export default function AIAnalysisTestResultJira({
  result,
}: AIAnalysisTestResultJiraProps) {
  const [copied, setCopied] =
    useState(false);

  const testResult = useMemo<TestResult>(
    () => {
      if (
        !result.test_result ||
        typeof result.test_result !== "object"
      ) {
        return {};
      }

      return result.test_result as TestResult;
    },
    [result.test_result],
  );

  const jiraDescription =
    result.jira_description?.trim() || "";

  const hasTestResult =
    Object.keys(testResult).length > 0;

  const hasJiraDescription =
    jiraDescription.length > 0;

  // ===========================================================================
  // TEST STATUS
  // ===========================================================================

  const testStatus =
    getTestStatus(testResult);

  // ===========================================================================
  // COPY JIRA
  // ===========================================================================

  const copyJiraDescription =
    async () => {
      if (!jiraDescription) {
        return;
      }

      try {
        await navigator.clipboard.writeText(
          jiraDescription,
        );

        setCopied(true);

        window.setTimeout(() => {
          setCopied(false);
        }, 1800);
      } catch {
        setCopied(false);
      }
    };

  return (
    <section className="space-y-6">

      {/* ==================================================================== */}
      {/* HEADER                                                               */}
      {/* ==================================================================== */}

      <div className="flex items-start gap-3">

        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-50 text-violet-600">
          ✓
        </div>

        <div>

          <h3 className="text-lg font-semibold text-slate-800">
            Test Result & Jira
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Validate the recommended resolution and prepare the
            analysis summary for Jira.
          </p>

        </div>

      </div>

      {/* ==================================================================== */}
      {/* TEST RESULT                                                          */}
      {/* ==================================================================== */}

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

        <div className="flex flex-wrap items-start justify-between gap-3">

          <div>

            <h4 className="text-sm font-semibold text-slate-800">
              Test Result
            </h4>

            <p className="mt-1 text-xs text-slate-400">
              Validation steps and expected outcome for the proposed fix.
            </p>

          </div>

          {hasTestResult && (
            <TestStatusBadge
              status={testStatus}
            />
          )}

        </div>

        {hasTestResult ? (
          <div className="mt-5 space-y-5">

            {/* ============================================================ */}
            {/* TEST CASE                                                     */}
            {/* ============================================================ */}

            {testResult.test_case && (
              <ResultBlock
                title="Test Case"
                value={
                  testResult.test_case
                }
              />
            )}

            {/* ============================================================ */}
            {/* EXPECTED RESULT                                               */}
            {/* ============================================================ */}

            {testResult.expected_result && (
              <ResultBlock
                title="Expected Result"
                value={
                  testResult.expected_result
                }
              />
            )}

            {/* ============================================================ */}
            {/* VERIFICATION STEPS                                            */}
            {/* ============================================================ */}

            {getSteps(testResult).length >
              0 && (
              <StepsList
                title="Verification Steps"
                steps={getSteps(
                  testResult,
                )}
              />
            )}

            {/* ============================================================ */}
            {/* ADDITIONAL STRUCTURED FIELDS                                  */}
            {/* ============================================================ */}

            <AdditionalTestFields
              testResult={testResult}
            />

          </div>
        ) : (
          <EmptyState
            title="Test result not available"
            description="No structured validation result was returned by the analysis."
          />
        )}

      </div>

      {/* ==================================================================== */}
      {/* JIRA DESCRIPTION                                                     */}
      {/* ==================================================================== */}

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

        <div className="flex flex-wrap items-start justify-between gap-3">

          <div>

            <h4 className="text-sm font-semibold text-slate-800">
              Jira Description
            </h4>

            <p className="mt-1 text-xs text-slate-400">
              Structured incident summary suitable for a Jira issue.
            </p>

          </div>

          {hasJiraDescription && (
            <button
              type="button"
              onClick={
                copyJiraDescription
              }
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 transition hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700"
            >
              {copied
                ? "Copied"
                : "Copy"}
            </button>
          )}

        </div>

        {hasJiraDescription ? (
          <div className="mt-5 overflow-hidden rounded-xl border border-slate-200 bg-slate-50">

            <div className="border-b border-slate-200 bg-white px-4 py-3">

              <div className="flex items-center gap-2">

                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                  #
                </div>

                <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Jira-ready summary
                </span>

              </div>

            </div>

            <div className="p-5">

              <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">
                {jiraDescription}
              </p>

            </div>

          </div>
        ) : (
          <EmptyState
            title="Jira description not available"
            description="The analysis did not return a Jira description."
          />
        )}

      </div>

      {/* ==================================================================== */}
      {/* VALIDATION SUMMARY                                                   */}
      {/* ==================================================================== */}

      {(hasTestResult ||
        hasJiraDescription) && (
        <ValidationSummary
          testStatus={testStatus}
          hasTestResult={
            hasTestResult
          }
          hasJiraDescription={
            hasJiraDescription
          }
        />
      )}

    </section>
  );
}

// =============================================================================
// TEST STATUS
// =============================================================================

function getTestStatus(
  testResult: TestResult,
): string {
  const status =
    testResult.status;

  if (
    typeof status === "string" &&
    status.trim()
  ) {
    return status.trim();
  }

  return "Available";
}

// =============================================================================
// TEST STATUS BADGE
// =============================================================================

interface TestStatusBadgeProps {
  status: string;
}

function TestStatusBadge({
  status,
}: TestStatusBadgeProps) {
  const normalized =
    status.toLowerCase();

  const isPass =
    normalized === "pass" ||
    normalized === "passed" ||
    normalized === "success" ||
    normalized === "successful";

  const isFail =
    normalized === "fail" ||
    normalized === "failed" ||
    normalized === "error";

  const className = isPass
    ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200"
    : isFail
      ? "bg-red-50 text-red-700 ring-1 ring-red-200"
      : "bg-amber-50 text-amber-700 ring-1 ring-amber-200";

  const icon = isPass
    ? "✓"
    : isFail
      ? "!"
      : "•";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold ${className}`}
    >
      <span>{icon}</span>
      {status}
    </span>
  );
}

// =============================================================================
// RESULT BLOCK
// =============================================================================

interface ResultBlockProps {
  title: string;
  value: string;
}

function ResultBlock({
  title,
  value,
}: ResultBlockProps) {
  return (
    <div>

      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
        {title}
      </p>

      <div className="mt-2 rounded-xl border border-slate-100 bg-slate-50 p-4">

        <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">
          {value}
        </p>

      </div>

    </div>
  );
}

// =============================================================================
// STEPS LIST
// =============================================================================

interface StepsListProps {
  title: string;
  steps: string[];
}

function StepsList({
  title,
  steps,
}: StepsListProps) {
  return (
    <div>

      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
        {title}
      </p>

      <div className="mt-3 space-y-2">

        {steps.map(
          (step, index) => (
            <div
              key={`${index}-${step}`}
              className="flex items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-3"
            >

              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-white text-xs font-bold text-indigo-600 ring-1 ring-slate-200">
                {index + 1}
              </div>

              <p className="pt-1 text-sm leading-6 text-slate-600">
                {step}
              </p>

            </div>
          ),
        )}

      </div>

    </div>
  );
}

// =============================================================================
// ADDITIONAL TEST FIELDS
// =============================================================================

interface AdditionalTestFieldsProps {
  testResult: TestResult;
}

function AdditionalTestFields({
  testResult,
}: AdditionalTestFieldsProps) {
  const excludedKeys = new Set([
    "status",
    "test_case",
    "expected_result",
    "verification_steps",
    "test_steps",
  ]);

  const fields = Object.entries(
    testResult,
  ).filter(
    ([key, value]) =>
      !excludedKeys.has(key) &&
      value !== null &&
      value !== undefined &&
      value !== "",
  );

  if (!fields.length) {
    return null;
  }

  return (
    <div>

      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
        Additional Validation Details
      </p>

      <div className="mt-3 grid gap-3 sm:grid-cols-2">

        {fields.map(
          ([key, value]) => (
            <div
              key={key}
              className="rounded-xl border border-slate-100 bg-slate-50 p-4"
            >

              <p className="text-xs font-medium text-slate-400">
                {formatLabel(key)}
              </p>

              <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                {formatValue(value)}
              </p>

            </div>
          ),
        )}

      </div>

    </div>
  );
}

// =============================================================================
// VALIDATION SUMMARY
// =============================================================================

interface ValidationSummaryProps {
  testStatus: string;
  hasTestResult: boolean;
  hasJiraDescription: boolean;
}

function ValidationSummary({
  testStatus,
  hasTestResult,
  hasJiraDescription,
}: ValidationSummaryProps) {
  const isPass =
    testStatus.toLowerCase() ===
      "pass" ||
    testStatus.toLowerCase() ===
      "passed";

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">

      <div className="flex items-start gap-3">

        <div
          className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
            isPass
              ? "bg-emerald-100 text-emerald-700"
              : "bg-indigo-100 text-indigo-700"
          }`}
        >
          {isPass ? "✓" : "i"}
        </div>

        <div className="min-w-0">

          <h4 className="text-sm font-semibold text-slate-800">
            Validation Summary
          </h4>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            {hasTestResult
              ? `Test result: ${testStatus}.`
              : "No structured test result was returned."}{" "}
            {hasJiraDescription
              ? "A Jira-ready description is available."
              : "No Jira description was returned."}
          </p>

        </div>

      </div>

    </div>
  );
}

// =============================================================================
// EMPTY STATE
// =============================================================================

interface EmptyStateProps {
  title: string;
  description: string;
}

function EmptyState({
  title,
  description,
}: EmptyStateProps) {
  return (
    <div className="mt-5 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-5">

      <p className="text-sm font-semibold text-slate-700">
        {title}
      </p>

      <p className="mt-1 text-sm leading-6 text-slate-500">
        {description}
      </p>

    </div>
  );
}

// =============================================================================
// FORMAT LABEL
// =============================================================================

function formatLabel(
  value: string,
): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) =>
      character.toUpperCase(),
    );
}

// =============================================================================
// FORMAT VALUE
// =============================================================================

function formatValue(
  value: unknown,
): string {
  if (
    typeof value === "string"
  ) {
    return value;
  }

  if (
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  try {
    return JSON.stringify(
      value,
      null,
      2,
    );
  } catch {
    return String(value);
  }
}

// =============================================================================
// GET STEPS
// =============================================================================

function getSteps(
  testResult: TestResult,
): string[] {
  if (
    Array.isArray(
      testResult.verification_steps,
    )
  ) {
    return testResult.verification_steps.filter(
      (step): step is string =>
        typeof step === "string" &&
        step.trim().length > 0,
    );
  }

  if (
    Array.isArray(
      testResult.test_steps,
    )
  ) {
    return testResult.test_steps.filter(
      (step): step is string =>
        typeof step === "string" &&
        step.trim().length > 0,
    );
  }

  return [];
}