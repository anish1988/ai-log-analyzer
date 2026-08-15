"use client";

import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { ExternalLink } from "lucide-react";

import type {
  AIAnalysisResponse,
} from "@/lib/types/aiAnalysis";

import AIAnalysisRagStatus from "./AIAnalysisRagStatus";
import AIAnalysisRootCauseEvidence from "./AIAnalysisRootCauseEvidence";
import AIAnalysisSolutionOptimization from "./AIAnalysisSolutionOptimization";
import AIAnalysisTestResultJira from "./AIAnalysisTestResultJira";

import {
  createJiraTicket,
  type JiraTicketCreateResponse,
} from "@/lib/api/jira";

// =============================================================================
// TYPES
// =============================================================================

interface AIAnalysisResultContainerProps {
  response: AIAnalysisResponse;
}

type ResultTab =
  | "overview"
  | "rag"
  | "root-cause"
  | "solution"
  | "validation";

// =============================================================================
// TABS
// =============================================================================

const tabs: Array<{
  id: ResultTab;
  label: string;
  shortLabel: string;
}> = [
  {
    id: "overview",
    label: "Overview",
    shortLabel: "Overview",
  },
  {
    id: "rag",
    label: "RAG Status",
    shortLabel: "RAG",
  },
  {
    id: "root-cause",
    label: "Root Cause & Evidence",
    shortLabel: "Root Cause",
  },
  {
    id: "solution",
    label: "Solution & Optimization",
    shortLabel: "Solution",
  },
  {
    id: "validation",
    label: "Test Result & Jira",
    shortLabel: "Validation",
  },
];

// =============================================================================
// COMPONENT
// =============================================================================

export default function AIAnalysisResultContainer({
  response,
}: AIAnalysisResultContainerProps) {
  const results =
    response.final_results ?? [];

  // ===========================================================================
  // SELECTION STATE
  // ===========================================================================

  const [
    selectedResultIndex,
    setSelectedResultIndex,
  ] = useState(0);

  const [
    activeTab,
    setActiveTab,
  ] = useState<ResultTab>("overview");

  // ===========================================================================
  // JIRA STATE
  // ===========================================================================

  /**
   * Error ID currently being used to create a Jira ticket.
   *
   * This makes the loading state individual to one error.
   */
  const [
    jiraCreatingErrorId,
    setJiraCreatingErrorId,
  ] = useState<string | null>(null);

  /**
   * Jira tickets created during this analysis session.
   *
   * Key:
   *   error_id
   *
   * Value:
   *   Jira ticket response
   *
   * This allows every error to maintain its own Jira state.
   */
  const [
    jiraTickets,
    setJiraTickets,
  ] = useState<
    Record<
      string,
      JiraTicketCreateResponse
    >
  >({});

  /**
   * Jira error message.
   */
  const [
    jiraError,
    setJiraError,
  ] = useState<string | null>(null);

  // ===========================================================================
  // SELECTED RESULT
  // ===========================================================================

  const selectedResult =
    results[selectedResultIndex];

  const selectedErrorCount =
    results.length;

  const selectedResultNumber =
    selectedResult
      ? selectedResultIndex + 1
      : 0;

  // ===========================================================================
  // SAFE RESULT INFORMATION
  // ===========================================================================

  const resultTitle = useMemo(() => {
    if (!selectedResult) {
      return "No analysis result";
    }

    return (
      selectedResult.title ||
      selectedResult.error_id ||
      `Error ${selectedResultNumber}`
    );
  }, [
    selectedResult,
    selectedResultNumber,
  ]);

  // ===========================================================================
  // CREATE JIRA TICKET
  // ===========================================================================

  const handleCreateJiraTicket =
    async () => {
      // -----------------------------------------------------------------------
      // Safety check
      // -----------------------------------------------------------------------

      if (!selectedResult) {
        return;
      }

      // -----------------------------------------------------------------------
      // Error ID
      // -----------------------------------------------------------------------

      const errorId =
        selectedResult.error_id;

      if (!errorId) {
        setJiraError(
          "Cannot create Jira ticket because the error ID is missing.",
        );

        return;
      }

      // -----------------------------------------------------------------------
      // Prevent duplicate ticket creation
      // -----------------------------------------------------------------------

      if (jiraTickets[errorId]) {
        return;
      }

      // -----------------------------------------------------------------------
      // Prevent duplicate clicks
      // -----------------------------------------------------------------------

      if (
        jiraCreatingErrorId ===
        errorId
      ) {
        return;
      }

      // -----------------------------------------------------------------------
      // Reset previous error
      // -----------------------------------------------------------------------

      setJiraError(null);

      // -----------------------------------------------------------------------
      // Set loading state for THIS error only
      // -----------------------------------------------------------------------

      setJiraCreatingErrorId(
        errorId,
      );

      try {
        console.log(
          "====================================",
        );

        console.log(
          "CREATING JIRA TICKET",
        );

        console.log(
          "Error ID:",
          errorId,
        );

        console.log(
          "Analysis:",
          selectedResult,
        );

        console.log(
          "====================================",
        );

        // ---------------------------------------------------------------------
        // Create Jira ticket
        // ---------------------------------------------------------------------

        const result =
          await createJiraTicket(
            selectedResult,
          );

        console.log(
          "====================================",
        );

        console.log(
          "JIRA TICKET CREATED",
        );

        console.log(
          "Error ID:",
          errorId,
        );

        console.log(
          "Issue Key:",
          result.issue_key,
        );

        console.log(
          "Issue URL:",
          result.issue_url,
        );

        console.log(
          "====================================",
        );

        // ---------------------------------------------------------------------
        // Store Jira result against THIS error
        // ---------------------------------------------------------------------

        setJiraTickets(
          (previous) => ({
            ...previous,
            [errorId]: result,
          }),
        );
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : "Failed to create Jira ticket.";

        console.error(
          "====================================",
        );

        console.error(
          "JIRA TICKET CREATION FAILED",
        );

        console.error(
          "Error ID:",
          errorId,
        );

        console.error(
          error,
        );

        console.error(
          "====================================",
        );

        setJiraError(
          message,
        );
      } finally {
        setJiraCreatingErrorId(
          null,
        );
      }
    };

  // ===========================================================================
  // EMPTY STATE
  // ===========================================================================

  if (!results.length) {
    return (
      <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="mx-auto max-w-xl text-center">

          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-400">
            —
          </div>

          <h2 className="mt-4 text-lg font-semibold text-slate-800">
            No AI analysis results
          </h2>

          <p className="mt-2 text-sm leading-6 text-slate-500">
            The analysis completed, but no individual
            error results were returned.
          </p>

        </div>
      </section>
    );
  }

  // ===========================================================================
  // MAIN UI
  // ===========================================================================

  return (
    <section className="space-y-6">

      {/* ==================================================================== */}
      {/* RESULT HEADER                                                        */}
      {/* ==================================================================== */}

      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">

        <div className="flex flex-wrap items-start justify-between gap-5 p-6">

          <div className="flex items-start gap-4">

            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
              ✦
            </div>

            <div>

              <div className="flex flex-wrap items-center gap-3">

                <h1 className="text-xl font-bold text-slate-800">
                  AI Analysis Results
                </h1>

                <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  Completed
                </span>

              </div>

              <p className="mt-1 text-sm text-slate-500">
                AI analysis completed for{" "}
                <span className="font-semibold text-slate-700">
                  {selectedErrorCount}
                </span>{" "}
                selected error
                {selectedErrorCount !== 1
                  ? "s"
                  : ""}
                .
              </p>

            </div>

          </div>

          {/* Summary */}

          <div className="flex items-center gap-3">

            <SummaryItem
              label="Analyzed"
              value={String(
                response.total_errors ??
                  selectedErrorCount,
              )}
            />

            <SummaryItem
              label="Completed"
              value={String(
                response.completed_errors ??
                  selectedErrorCount,
              )}
            />

            <SummaryItem
              label="Progress"
              value={`${response.progress ?? 100}%`}
              success
            />

          </div>

        </div>

      </div>

      {/* ==================================================================== */}
      {/* MAIN RESULT LAYOUT                                                   */}
      {/* ==================================================================== */}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">

        {/* ================================================================== */}
        {/* LEFT ERROR LIST                                                    */}
        {/* ================================================================== */}

        <aside className="lg:col-span-3">

          <div className="sticky top-6 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

            {/* List header */}

            <div className="border-b border-slate-200 px-5 py-4">

              <div className="flex items-center justify-between">

                <div>

                  <h2 className="text-sm font-semibold text-slate-800">
                    Analyzed Errors
                  </h2>

                  <p className="mt-1 text-xs text-slate-400">
                    Select an error to review
                  </p>

                </div>

                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">
                  {selectedErrorCount}
                </span>

              </div>

            </div>

            {/* Error list */}

            <div className="max-h-[calc(100vh-260px)] overflow-y-auto p-2">

              {results.map(
                (result, index) => {
                  const isSelected =
                    index ===
                    selectedResultIndex;

                  return (
                    <button
                      key={
                        result.error_id ??
                        `result-${index}`
                      }
                      type="button"
                      onClick={() => {
                        setSelectedResultIndex(
                          index,
                        );

                        setActiveTab(
                          "overview",
                        );

                        // Clear only the previous
                        // global error message.
                        setJiraError(null);
                      }}
                      className={`mb-1 w-full rounded-xl p-3 text-left transition ${
                        isSelected
                          ? "bg-indigo-50 ring-1 ring-indigo-100"
                          : "hover:bg-slate-50"
                      }`}
                    >

                      <div className="flex items-start gap-3">

                        {/* Status */}

                        <span
                          className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${
                            result.status ===
                            "completed"
                              ? "bg-emerald-500"
                              : result.error
                                ? "bg-red-500"
                                : "bg-slate-300"
                          }`}
                        />

                        <div className="min-w-0 flex-1">

                          <div className="flex items-center justify-between gap-2">

                            <span
                              className={`truncate text-xs font-semibold ${
                                isSelected
                                  ? "text-indigo-700"
                                  : "text-slate-700"
                              }`}
                            >
                              {result.error_id ||
                                `Error ${index + 1}`}
                            </span>

                            <span className="shrink-0 text-[10px] font-medium text-slate-400">
                              {index + 1}
                            </span>

                          </div>

                          <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-500">
                            {result.title ||
                              "No error title available"}
                          </p>

                          <div className="mt-2 flex flex-wrap gap-1.5">

                            {result.log_type && (
                              <span className="rounded-md bg-white px-1.5 py-0.5 text-[10px] font-medium text-slate-400 ring-1 ring-slate-100">
                                {result.log_type}
                              </span>
                            )}

                            {result.severity && (
                              <span className="rounded-md bg-white px-1.5 py-0.5 text-[10px] font-medium text-slate-400 ring-1 ring-slate-100">
                                {result.severity}
                              </span>
                            )}

                          </div>

                        </div>

                      </div>

                    </button>
                  );
                },
              )}

            </div>

          </div>

        </aside>

        {/* ================================================================== */}
        {/* RIGHT RESULT AREA                                                  */}
        {/* ================================================================== */}

        <div className="min-w-0 lg:col-span-9">

          {selectedResult && (
            <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

              {/* ============================================================ */}
              {/* SELECTED ERROR HEADER                                        */}
              {/* ============================================================ */}

              <div className="border-b border-slate-200 bg-gradient-to-r from-slate-50 via-white to-indigo-50/40 px-6 py-5">

                <div className="flex flex-wrap items-start justify-between gap-4">

                  <div className="min-w-0 flex-1">

                    <div className="flex flex-wrap items-center gap-2">

                      <span className="rounded-md bg-indigo-50 px-2 py-1 font-mono text-xs font-semibold text-indigo-700">
                        {selectedResult.error_id}
                      </span>

                      {selectedResult.log_type && (
                        <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-500">
                          {selectedResult.log_type}
                        </span>
                      )}

                      {selectedResult.server && (
                        <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-500">
                          {selectedResult.server}
                        </span>
                      )}

                    </div>

                    {/* ------------------------------------------------------ */}
                    {/* ERROR TITLE + JIRA BUTTON                             */}
                    {/* ------------------------------------------------------ */}

                    <div className="mt-3 flex flex-wrap items-center justify-between gap-3">

                      <div className="min-w-0">

                        <h2 className="text-lg font-semibold leading-7 text-slate-800">
                          {resultTitle}
                        </h2>

                        <p className="mt-1 text-xs text-slate-400">
                          Error {selectedResultNumber} of{" "}
                          {selectedErrorCount}
                        </p>

                      </div>

                      {/* ---------------------------------------------------- */}
                      {/* INDIVIDUAL JIRA ACTION                              */}
                      {/* ---------------------------------------------------- */}

                      <div className="flex shrink-0 items-center gap-2">

                        {(() => {
                          const errorId =
                            selectedResult.error_id;

                          const jiraTicket =
                            errorId
                              ? jiraTickets[
                                  errorId
                                ]
                              : undefined;

                          const isCreating =
                            errorId ===
                            jiraCreatingErrorId;

                          if (
                            jiraTicket
                          ) {
                            return (
                              <>
                                <span className="inline-flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700">
                                  <span className="h-2 w-2 rounded-full bg-emerald-500" />

                                  {jiraTicket.issue_key}
                                </span>

                                <a
                                  href={
                                    jiraTicket.issue_url
                                  }
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50"
                                >
                                  Open Jira

                                  <ExternalLink
                                    size={14}
                                  />
                                </a>
                              </>
                            );
                          }

                          return (
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              disabled={
                                isCreating
                              }
                              onClick={
                                handleCreateJiraTicket
                              }
                              className="gap-2"
                            >
                              <ExternalLink
                                size={16}
                              />

                              {isCreating
                                ? "Creating..."
                                : "Create Jira Ticket"}
                            </Button>
                          );
                        })()}

                      </div>

                    </div>

                  </div>

                  {/* Analysis Status */}

                  <span
                    className={`rounded-full px-3 py-1.5 text-xs font-semibold ${
                      selectedResult.status ===
                      "completed"
                        ? "bg-emerald-50 text-emerald-700"
                        : selectedResult.error
                          ? "bg-red-50 text-red-700"
                          : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {selectedResult.status ===
                    "completed"
                      ? "Analysis Complete"
                      : selectedResult.error
                        ? "Analysis Error"
                        : "Analysis Available"}
                  </span>

                </div>

              </div>

              {/* ============================================================ */}
              {/* JIRA ERROR                                                    */}
              {/* ============================================================ */}

              {jiraError && (
                <div className="border-b border-red-100 bg-red-50 px-6 py-3 text-sm text-red-700">

                  <span className="font-semibold">
                    Jira ticket creation failed:
                  </span>{" "}

                  {jiraError}

                </div>
              )}

              {/* ============================================================ */}
              {/* TABS                                                          */}
              {/* ============================================================ */}

              <div className="border-b border-slate-200 px-4 pt-3">

                <div
                  className="flex gap-1 overflow-x-auto"
                  role="tablist"
                  aria-label="AI analysis sections"
                >

                  {tabs.map(
                    (tab) => {
                      const isActive =
                        activeTab ===
                        tab.id;

                      return (
                        <button
                          key={tab.id}
                          type="button"
                          role="tab"
                          aria-selected={
                            isActive
                          }
                          onClick={() =>
                            setActiveTab(
                              tab.id,
                            )
                          }
                          className={`relative whitespace-nowrap rounded-t-lg px-4 py-3 text-sm font-medium transition ${
                            isActive
                              ? "bg-indigo-50 text-indigo-700"
                              : "text-slate-500 hover:bg-slate-50 hover:text-slate-700"
                          }`}
                        >

                          <span className="hidden sm:inline">
                            {tab.label}
                          </span>

                          <span className="sm:hidden">
                            {tab.shortLabel}
                          </span>

                          {isActive && (
                            <span className="absolute inset-x-3 -bottom-px h-0.5 rounded-full bg-indigo-600" />
                          )}

                        </button>
                      );
                    },
                  )}

                </div>

              </div>

              {/* ============================================================ */}
              {/* TAB CONTENT                                                   */}
              {/* ============================================================ */}

              <div className="p-6">

                {/* ---------------------------------------------------------- */}
                {/* OVERVIEW                                                     */}
                {/* ---------------------------------------------------------- */}

                {activeTab ===
                  "overview" && (
                  <OverviewTab
                    result={
                      selectedResult
                    }
                  />
                )}

                {/* ---------------------------------------------------------- */}
                {/* RAG                                                          */}
                {/* ---------------------------------------------------------- */}

                {activeTab === "rag" && (
                  <AIAnalysisRagStatus
                    result={
                      selectedResult
                    }
                  />
                )}

                {/* ---------------------------------------------------------- */}
                {/* ROOT CAUSE + EVIDENCE                                        */}
                {/* ---------------------------------------------------------- */}

                {activeTab ===
                  "root-cause" && (
                  <AIAnalysisRootCauseEvidence
                    result={
                      selectedResult
                    }
                  />
                )}

                {/* ---------------------------------------------------------- */}
                {/* SOLUTION + OPTIMIZATION                                     */}
                {/* ---------------------------------------------------------- */}

                {activeTab ===
                  "solution" && (
                  <AIAnalysisSolutionOptimization
                    result={
                      selectedResult
                    }
                  />
                )}

                {/* ---------------------------------------------------------- */}
                {/* TEST + JIRA                                                  */}
                {/* ---------------------------------------------------------- */}

                {activeTab ===
                  "validation" && (
                  <AIAnalysisTestResultJira
                    result={
                      selectedResult
                    }
                  />
                )}

              </div>

            </div>
          )}

        </div>

      </div>

    </section>
  );
}

// =============================================================================
// OVERVIEW TAB
// =============================================================================

interface OverviewTabProps {
  result: NonNullable<
    AIAnalysisResponse["final_results"]
  >[number];
}

function OverviewTab({
  result,
}: OverviewTabProps) {
  return (
    <div className="space-y-6">

      {/* Summary */}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <InfoCard
          label="Severity"
          value={
            result.severity ||
            "Unknown"
          }
        />

        <InfoCard
          label="Source"
          value={
            result.source ||
            "Unknown"
          }
        />

        <InfoCard
          label="RAG"
          value={
            result.rag_match
              ? "Historical match found"
              : "No historical match"
          }
        />

        <InfoCard
          label="Confidence"
          value={
            result.confidence ||
            "Not available"
          }
        />

      </div>

      {/* Root cause preview */}

      {result.root_cause && (
        <ContentCard
          title="Root Cause"
          value={
            result.root_cause
          }
        />
      )}

      {/* Solution preview */}

      {result.solution && (
        <ContentCard
          title="Recommended Solution"
          value={
            result.solution
          }
        />
      )}

      {/* Source information */}

      {(result.source_file ||
        result.source_line_number !==
          null ||
        result.source_code_analysis) && (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">

          <h3 className="text-sm font-semibold text-slate-800">
            Source Analysis
          </h3>

          <div className="mt-4 grid gap-3 sm:grid-cols-2">

            {result.source_file && (
              <InfoCard
                label="Source File"
                value={
                  result.source_file
                }
              />
            )}

            {result.source_line_number !==
              null && (
              <InfoCard
                label="Source Line"
                value={String(
                  result.source_line_number,
                )}
              />
            )}

          </div>

          {result.source_code_analysis && (
            <div className="mt-4">
              <ContentCard
                title="Analysis"
                value={
                  result.source_code_analysis
                }
              />
            </div>
          )}

        </div>
      )}

    </div>
  );
}

// =============================================================================
// SMALL UI COMPONENTS
// =============================================================================

interface SummaryItemProps {
  label: string;
  value: string;
  success?: boolean;
}

function SummaryItem({
  label,
  value,
  success = false,
}: SummaryItemProps) {
  return (
    <div className="min-w-[76px] rounded-xl border border-slate-100 bg-slate-50 px-3 py-2">

      <p className="text-[10px] font-medium uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p
        className={`mt-1 text-sm font-bold ${
          success
            ? "text-emerald-600"
            : "text-slate-800"
        }`}
      >
        {value}
      </p>

    </div>
  );
}

interface InfoCardProps {
  label: string;
  value: string;
}

function InfoCard({
  label,
  value,
}: InfoCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">

      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p className="mt-2 break-words text-sm font-semibold text-slate-700">
        {value}
      </p>

    </div>
  );
}

interface ContentCardProps {
  title: string;
  value: string;
}

function ContentCard({
  title,
  value,
}: ContentCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">

      <h3 className="text-sm font-semibold text-slate-800">
        {title}
      </h3>

      <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">
        {value}
      </p>

    </div>
  );
}