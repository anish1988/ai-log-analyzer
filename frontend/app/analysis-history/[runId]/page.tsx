"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  ArrowLeft,
  CircleAlert,
  ChevronRight,
  Clock3,
  FileText,
  History,
  Server,
} from "lucide-react";

import {
  getAnalysisRunDetail,
  type AnalysisResult,
  type AnalysisRun,
} from "@/lib/api/analysisHistory";

interface AnalysisRunDetailPageProps {
  params: Promise<{
    runId: string;
  }>;
}

function formatDate(value: string | null): string {
  if (!value) {
    return "—";
  }

  return new Date(value).toLocaleString();
}

function formatSource(source: AnalysisRun["source_type"]): string {
  return source === "automation" ? "Automation" : "Manual";
}

function statusClasses(status: AnalysisRun["status"]): string {
  switch (status) {
    case "completed":
      return "bg-emerald-50 text-emerald-700";
    case "failed":
    case "error":
      return "bg-red-50 text-red-700";
    case "processing":
      return "bg-amber-50 text-amber-700";
    default:
      return "bg-slate-100 text-slate-600";
  }
}

function resultStatusClasses(
  status: AnalysisResult["analysis_status"],
): string {
  if (!status) {
    return "bg-slate-100 text-slate-600";
  }

  const normalizedStatus = status.toLowerCase();

  if (
    normalizedStatus.includes("complete") ||
    normalizedStatus.includes("success")
  ) {
    return "bg-emerald-50 text-emerald-700";
  }

  if (
    normalizedStatus.includes("fail") ||
    normalizedStatus.includes("error")
  ) {
    return "bg-red-50 text-red-700";
  }

  return "bg-amber-50 text-amber-700";
}

function jiraLabel(result: AnalysisResult): string {
  if (result.jira_issue_key) {
    return result.jira_issue_key;
  }

  return "Not created";
}

export default function AnalysisRunDetailPage({
  params,
}: AnalysisRunDetailPageProps) {
  const [run, setRun] = useState<AnalysisRun | null>(null);
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadRun() {
      try {
        setLoading(true);
        setError(null);

        const { run: runData, results: resultData } =
          await getAnalysisRunDetail((await params).runId);

        if (!cancelled) {
          setRun(runData);
          setResults(resultData);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load analysis run.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadRun();

    return () => {
      cancelled = true;
    };
  }, [params]);

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <div className="mb-6">
        <Link
          href="/analysis-history"
          className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Analysis History
        </Link>
      </div>

      <div className="mb-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50">
            <History className="h-5 w-5 text-indigo-600" />
          </div>

          <div>
            <h1 className="text-2xl font-semibold text-slate-900">
              Analysis Run
            </h1>

            <p className="mt-1 text-sm text-slate-500">
              Review the analysis execution and its analyzed errors.
            </p>
          </div>
        </div>
      </div>

      {loading && (
        <section className="rounded-xl border border-slate-200 bg-white px-5 py-12 text-center">
          <Clock3 className="mx-auto h-8 w-8 animate-pulse text-indigo-400" />

          <p className="mt-3 text-sm font-medium text-slate-700">
            Loading analysis run...
          </p>
        </section>
      )}

      {!loading && error && (
        <section className="rounded-xl border border-slate-200 bg-white px-5 py-12 text-center">
          <CircleAlert className="mx-auto h-8 w-8 text-red-400" />

          <p className="mt-3 text-sm font-medium text-red-600">
            Failed to load analysis run.
          </p>

          <p className="mt-1 text-sm text-slate-500">{error}</p>
        </section>
      )}

      {!loading && !error && run && (
        <>
          <section className="mb-6 overflow-hidden rounded-xl border border-slate-200 bg-white">
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50">
                  <FileText className="h-4 w-4 text-indigo-600" />
                </div>

                <div>
                  <h2 className="text-sm font-semibold text-slate-900">
                    Run Summary
                  </h2>

                  <p className="text-xs text-slate-500">
                    Analysis execution details
                  </p>
                </div>
              </div>

              <span
                className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${statusClasses(
                  run.status,
                )}`}
              >
                {run.status}
              </span>
            </div>

            <div className="grid grid-cols-1 divide-y divide-slate-100 md:grid-cols-2 md:divide-x md:divide-y-0">
              <div className="grid grid-cols-2">
                <div className="border-b border-slate-100 px-5 py-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Date
                  </p>
                  <p className="mt-1 text-sm text-slate-700">
                    {formatDate(run.created_at)}
                  </p>
                </div>

                <div className="border-b border-slate-100 px-5 py-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Source
                  </p>
                  <p className="mt-1 text-sm text-slate-700">
                    {formatSource(run.source_type)}
                  </p>
                </div>

                <div className="px-5 py-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Log Type
                  </p>
                  <p className="mt-1 text-sm text-slate-700">
                    {run.log_type ?? "—"}
                  </p>
                </div>

                <div className="px-5 py-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Request ID
                  </p>
                  <p
                    className="mt-1 truncate text-sm text-slate-700"
                    title={run.request_id ?? undefined}
                  >
                    {run.request_id ?? "—"}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-3">
                <div className="px-5 py-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Errors
                  </p>
                  <p className="mt-1 text-lg font-semibold text-slate-900">
                    {run.total_errors}
                  </p>
                </div>

                <div className="px-5 py-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Completed
                  </p>
                  <p className="mt-1 text-lg font-semibold text-emerald-600">
                    {run.completed_errors}
                  </p>
                </div>

                <div className="px-5 py-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Failed
                  </p>
                  <p className="mt-1 text-lg font-semibold text-red-600">
                    {run.failed_errors}
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section className="overflow-hidden rounded-xl border border-slate-200 bg-white">
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50">
                  <Server className="h-4 w-4 text-indigo-600" />
                </div>

                <div>
                  <h2 className="text-sm font-semibold text-slate-900">
                    Analyzed Errors
                  </h2>

                  <p className="text-xs text-slate-500">
                    Individual errors processed during this run
                  </p>
                </div>
              </div>

              <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                {results.length}{" "}
                {results.length === 1 ? "result" : "results"}
              </span>
            </div>

            {results.length === 0 ? (
              <div className="px-5 py-12 text-center">
                <FileText className="mx-auto h-8 w-8 text-slate-300" />

                <p className="mt-3 text-sm font-medium text-slate-700">
                  No analyzed errors found.
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  This analysis run does not contain any individual results.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[1100px]">
                  <thead className="border-b border-slate-100 bg-slate-50">
                    <tr>
                      <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                        Error ID
                      </th>
                      <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                        Title
                      </th>
                      <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                        Server
                      </th>
                      <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                        Severity
                      </th>
                      <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                        Status
                      </th>
                      <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                        Jira
                      </th>
                      <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                        RAG
                      </th>
                      <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                        View Details
                       </th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-100">
                    {results.map((result) => (
                      <tr
                        key={result.id}
                        className="transition-colors hover:bg-slate-50"
                      >
                        <td className="whitespace-nowrap px-5 py-4 text-sm font-medium text-slate-700">
                          {result.error_id}
                        </td>

                        <td className="max-w-[320px] px-5 py-4">
                          <p
                            className="truncate text-sm text-slate-700"
                            title={result.title ?? undefined}
                          >
                            {result.title ?? result.error_summary ?? "—"}
                          </p>
                        </td>

                        <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-700">
                          {result.server ?? "—"}
                        </td>

                        <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-700">
                          {result.severity ?? "—"}
                        </td>

                        <td className="whitespace-nowrap px-5 py-4">
                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${resultStatusClasses(
                              result.analysis_status,
                            )}`}
                          >
                            {result.analysis_status ?? "Unknown"}
                          </span>
                        </td>

                        <td className="whitespace-nowrap px-5 py-4">
                          {result.jira_issue_url ? (
                            <a
                              href={result.jira_issue_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-sm font-medium text-indigo-600 hover:text-indigo-700 hover:underline"
                            >
                              {jiraLabel(result)}
                            </a>
                          ) : (
                            <span className="text-sm text-slate-500">
                              {jiraLabel(result)}
                            </span>
                          )}
                        </td>

                        <td className="whitespace-nowrap px-5 py-4">
                            {result.rag_match ? (
                                <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
                                Match
                                </span>
                            ) : (
                                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                                No Match
                                </span>
                            )}
                            </td>

                            <td className="whitespace-nowrap px-5 py-4">
                            <Link
                                href={`/analysis-history/${run.id}/results/${result.id}`}
                                className="inline-flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium text-indigo-600 transition-colors hover:bg-indigo-50"
                            >
                                View Details
                                <ChevronRight className="h-4 w-4" />
                            </Link>
                            </td>

                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
