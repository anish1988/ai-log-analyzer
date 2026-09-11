"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, History } from "lucide-react";

import {
  getAnalysisRunDetail,
  type AnalysisResult,
} from "@/lib/api/analysisHistory";
import type { JiraTicketCreateResponse } from "@/lib/api/jira";
import AIAnalysisResultContainer from "@/components/analysis/ai-analysis/AIAnalysisResultContainer";
import type {
  AIAnalysisResponse,
  AIAnalysisResult,
} from "@/lib/types/aiAnalysis";

interface AnalysisResultDetailPageProps {
  params: Promise<{
    runId: string;
    resultId: string;
  }>;
}

function toAIAnalysisResult(
  result: AnalysisResult,
): AIAnalysisResult {
  return {
    error_id: result.error_id,
    tier: result.tier ?? "",
    log_type: result.log_type ?? "",
    server: result.server ?? "",
    file_name: result.file_name ?? "",
    title: result.title ?? "",
    severity: result.severity ?? "",
    timestamp: result.timestamp ?? "",
    start_line: result.start_line,
    end_line: result.end_line,
    source: result.source ?? "",
    rag_match: result.rag_match,
    rag_knowledge_id: result.rag_knowledge_id,
    rag_similarity: result.rag_similarity,
    confidence: result.confidence ?? "",
    analysis_status: result.analysis_status ?? undefined,
    error_summary: result.error_summary ?? undefined,
    root_cause: result.root_cause ?? "",
    root_cause_evidence: Array.isArray(
      result.root_cause_evidence,
    )
      ? result.root_cause_evidence.map(
          (item) => ({
            line_number:
              typeof item === "object" &&
              item !== null &&
              "line_number" in item &&
              typeof item.line_number === "number"
                ? item.line_number
                : null,
            content:
              typeof item === "object" &&
              item !== null &&
              "content" in item &&
              typeof item.content === "string"
                ? item.content
                : "",
            explanation:
              typeof item === "object" &&
              item !== null &&
              "explanation" in item &&
              typeof item.explanation === "string"
                ? item.explanation
                : "",
          }),
        )
      : [],
    solution: result.solution ?? "",
    optimization: result.optimization ?? "",
    source_code_analysis:
      result.source_code_analysis ?? "",
    source_file: result.source_file,
    source_line_number:
      result.source_line_number,
    test_result: {
      ...(result.test_result ?? {}),
    },
    jira_description:
      result.jira_description ?? "",
    evidence: Array.isArray(result.evidence)
      ? result.evidence.map(
          (item) => ({
            line_number:
              typeof item === "object" &&
              item !== null &&
              "line_number" in item &&
              typeof item.line_number === "number"
                ? item.line_number
                : null,
            content:
              typeof item === "object" &&
              item !== null &&
              "content" in item &&
              typeof item.content === "string"
                ? item.content
                : "",
            explanation:
              typeof item === "object" &&
              item !== null &&
              "explanation" in item &&
              typeof item.explanation === "string"
                ? item.explanation
                : "",
          }),
        )
      : [],
    status:
      result.analysis_status ??
      "completed",
    error: null,
  };
}

export default function AnalysisResultDetailPage({
  params,
}: AnalysisResultDetailPageProps) {
  const [result, setResult] =
    useState<AnalysisResult | null>(null);
  const [runId, setRunId] = useState<string>("");
  const [loading, setLoading] =
    useState(true);
  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadResult() {
      try {
        setLoading(true);
        setError(null);

        const resolvedParams = await params;

        const detail =
          await getAnalysisRunDetail(
            resolvedParams.runId,
          );

        const resultId =
          Number(resolvedParams.resultId);

        if (
          !Number.isInteger(resultId) ||
          resultId <= 0
        ) {
          throw new Error(
            "Invalid analysis result ID.",
          );
        }

        const selectedResult =
          detail.results.find(
            (item) => item.id === resultId,
          );

        if (!selectedResult) {
          throw new Error(
            "Analysis result was not found.",
          );
        }

        if (!cancelled) {
          setRunId(resolvedParams.runId);
          setResult(selectedResult);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load analysis result.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadResult();

    return () => {
      cancelled = true;
    };
  }, [params]);

  const aiResult = result
    ? toAIAnalysisResult(result)
    : null;

  const response: AIAnalysisResponse | null =
    aiResult
      ? {
          request_id: "",
          analysis_run_id: runId,
          status: "completed",
          current_task: "Analysis completed",
          progress: 100,
          total_errors: 1,
          completed_errors: 1,
          final_results: [aiResult],
          progress_events: [],
          messages: [],
          error: null,
        }
      : null;

    const initialJiraTickets: Record<
        string,
        JiraTicketCreateResponse
        > =
        result?.jira_issue_key &&
        result.jira_issue_url
            ? {
                [result.error_id]: {
                success: true,
                error_id: result.error_id,
                issue_key: result.jira_issue_key,
                issue_id:
                    result.jira_issue_id ?? "",
                issue_url: result.jira_issue_url,
                message:
                    "Jira ticket loaded from analysis history.",
                },
            }
            : {};  

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <div className="mb-6">
        <Link
          href={`/analysis-history/${runId}`}
          className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Analysis Run
        </Link>
      </div>

      <div className="mb-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50">
            <History className="h-5 w-5 text-indigo-600" />
          </div>

          <div>
            <h1 className="text-2xl font-semibold text-slate-900">
              Analysis Result
            </h1>

            <p className="mt-1 text-sm text-slate-500">
              Review the complete AI analysis for this error.
            </p>
          </div>
        </div>
      </div>

      {loading && (
        <div className="rounded-xl border border-slate-200 bg-white px-5 py-12 text-center">
          <p className="text-sm text-slate-500">
            Loading analysis result...
          </p>
        </div>
      )}

      {!loading && error && (
        <div className="rounded-xl border border-red-200 bg-white px-5 py-12 text-center">
          <p className="text-sm font-medium text-red-600">
            Failed to load analysis result.
          </p>

          <p className="mt-1 text-sm text-slate-500">
            {error}
          </p>
        </div>
      )}

      {!loading && !error && response && (
        <AIAnalysisResultContainer
          response={response}
          singleResult
          initialJiraTickets={
                initialJiraTickets
          }
        />
      )}
    </div>
  );
}