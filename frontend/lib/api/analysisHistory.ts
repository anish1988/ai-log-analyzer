const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

export type AnalysisSourceType = "manual" | "automation";

export type AnalysisRunStatus =
  | "processing"
  | "completed"
  | "failed"
  | "error";

export interface AnalysisRun {
  id: string;
  request_id: string | null;
  user_id: string;
  source_type: AnalysisSourceType;
  status: AnalysisRunStatus;
  started_at: string | null;
  completed_at: string | null;
  total_errors: number;
  completed_errors: number;
  failed_errors: number;
  log_type: string | null;
  servers: unknown[];
  log_files: unknown[];
  custom_prompt: string | null;
  automation_run_id: string | null;
  metadata: Record<string, unknown>;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface AnalysisResult {
  id: number;
  analysis_run_id: string;
  error_id: string;
  error_signature: string | null;
  tier: string | null;
  log_type: string | null;
  server: string | null;
  file_name: string | null;
  file_path: string | null;
  title: string | null;
  severity: string | null;
  timestamp: string | null;
  start_line: number | null;
  end_line: number | null;
  source: string | null;
  rag_match: boolean;
  rag_knowledge_id: number | null;
  rag_similarity: number | null;
  confidence: string | null;
  analysis_status: string | null;
  error_summary: string | null;
  root_cause: string | null;
  solution: string | null;
  optimization: string | null;
  source_code_analysis: string | null;
  source_file: string | null;
  source_line_number: number | null;
  jira_description: string | null;
  jira_issue_key: string | null;
  jira_issue_id: string | null;
  jira_issue_url: string | null;
  jira_status: string | null;
  root_cause_evidence: unknown[];
  test_result: Record<string, unknown>;
  evidence: unknown[];
  source_code_location: Record<string, unknown>;
  missing_information: unknown[];
  request_payload: Record<string, unknown>;
  response_payload: Record<string, unknown>;
  jira_payload: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface AnalysisRunListResponse {
  items: AnalysisRun[];
  total: number;
}

export interface AnalysisRunDetailResponse {
  run: AnalysisRun;
  results: AnalysisResult[];
}

/**
 * Fetch the current user's analysis history.
 */
export async function getAnalysisRuns(
  limit = 50,
  offset = 0,
): Promise<AnalysisRunListResponse> {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });

  const response = await fetch(
    `${API_BASE_URL}/api/analysis-history?${params.toString()}`,
  );

  if (!response.ok) {
    let message =
      `Failed to fetch analysis history ` +
      `(HTTP ${response.status}).`;

    try {
      const errorBody = (await response.json()) as {
        detail?: unknown;
      };

      if (typeof errorBody.detail === "string") {
        message = errorBody.detail;
      }
    } catch {
      // Keep default HTTP error.
    }

    throw new Error(message);
  }

  return (await response.json()) as AnalysisRunListResponse;
}

/**
 * Fetch one analysis run and all of its results.
 */
export async function getAnalysisRunDetail(
  runId: string,
): Promise<AnalysisRunDetailResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/analysis-history/${encodeURIComponent(runId)}`,
  );

  if (!response.ok) {
    let message =
      `Failed to fetch analysis run ` +
      `(HTTP ${response.status}).`;

    try {
      const errorBody = (await response.json()) as {
        detail?: unknown;
      };

      if (typeof errorBody.detail === "string") {
        message = errorBody.detail;
      }
    } catch {
      // Keep default HTTP error.
    }

    throw new Error(message);
  }

  return (await response.json()) as AnalysisRunDetailResponse;
}