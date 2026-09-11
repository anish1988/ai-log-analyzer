"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Activity, ChevronRight, History } from "lucide-react";

import {
  getAnalysisRuns,
  type AnalysisRun,
} from "@/lib/api/analysisHistory";

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

export default function AnalysisHistoryPage() {
  const [runs, setRuns] = useState<AnalysisRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadHistory() {
      try {
        setLoading(true);
        setError(null);

        const response = await getAnalysisRuns();

        if (!cancelled) {
          setRuns(response.items);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load analysis history.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadHistory();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50">
            <History className="h-5 w-5 text-indigo-600" />
          </div>

          <div>
            <h1 className="text-2xl font-semibold text-slate-900">
              Analysis History
            </h1>

            <p className="mt-1 text-sm text-slate-500">
              View your previous AI analysis runs and results.
            </p>
          </div>
        </div>
      </div>

      <section className="overflow-hidden rounded-xl border border-slate-200 bg-white">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50">
              <Activity className="h-4 w-4 text-indigo-600" />
            </div>

            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Analysis Runs
              </h2>

              <p className="text-xs text-slate-500">
                Your latest analysis executions
              </p>
            </div>
          </div>

          {!loading && !error && (
            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
              {runs.length} {runs.length === 1 ? "run" : "runs"}
            </span>
          )}
        </div>

        {loading && (
          <div className="px-5 py-12 text-center text-sm text-slate-500">
            Loading analysis history...
          </div>
        )}

        {!loading && error && (
          <div className="px-5 py-12 text-center">
            <p className="text-sm font-medium text-red-600">
              Failed to load analysis history.
            </p>
            <p className="mt-1 text-sm text-slate-500">{error}</p>
          </div>
        )}

        {!loading && !error && runs.length === 0 && (
          <div className="px-5 py-12 text-center">
            <History className="mx-auto h-8 w-8 text-slate-300" />

            <p className="mt-3 text-sm font-medium text-slate-700">
              No analysis history found.
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Completed analysis runs will appear here.
            </p>
          </div>
        )}

        {!loading && !error && runs.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[900px]">
              <thead className="border-b border-slate-100 bg-slate-50">
                <tr>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Date
                  </th>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Source
                  </th>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Log Type
                  </th>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Errors
                  </th>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Completed
                  </th>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Failed
                  </th>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Status
                  </th>
                  <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Action
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-100">
                {runs.map((run) => (
                  <tr
                    key={run.id}
                    className="transition-colors hover:bg-slate-50"
                  >
                    <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-700">
                      {formatDate(run.created_at)}
                    </td>

                    <td className="px-5 py-4">
                      <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium capitalize text-slate-600">
                        {formatSource(run.source_type)}
                      </span>
                    </td>

                    <td className="px-5 py-4 text-sm text-slate-700">
                      {run.log_type ?? "—"}
                    </td>

                    <td className="px-5 py-4 text-sm font-medium text-slate-700">
                      {run.total_errors}
                    </td>

                    <td className="px-5 py-4 text-sm text-emerald-700">
                      {run.completed_errors}
                    </td>

                    <td className="px-5 py-4 text-sm text-red-600">
                      {run.failed_errors}
                    </td>

                    <td className="px-5 py-4">
                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${statusClasses(
                          run.status,
                        )}`}
                      >
                        {run.status}
                      </span>
                    </td>

                    <td className="px-5 py-4 text-right">
                     <Link
                        href={`/analysis-history/${run.id}`}
                        className="inline-flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium text-indigo-600 transition-colors hover:bg-indigo-50"
                        >
                        View
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
    </div>
  );
}