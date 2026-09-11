import type {
  AIAnalysisResult,
} from "@/lib/types/aiAnalysis";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

export interface JiraTicketCreateResponse {
  success: boolean;
  error_id: string;
  issue_key: string;
  issue_id: string;
  issue_url: string;
  message: string;
}

interface JiraTicketCreateRequest {
  analysis_run_id: string;
  analysis: AIAnalysisResult;
}

/**
 * Create one Jira ticket for one AI analysis result.
 *
 * Important:
 * This function accepts ONE analysis result only.
 */
export async function createJiraTicket(
  analysis: AIAnalysisResult,
  analysisRunId: string,
): Promise<JiraTicketCreateResponse> {
  const requestBody: JiraTicketCreateRequest = {
    analysis_run_id: analysisRunId,
    analysis,
  };

  const response = await fetch(
    `${API_BASE_URL}/api/ai/jira/ticket`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify(
        requestBody,
      ),
    },
  );

  if (!response.ok) {
    let message =
      `Failed to create Jira ticket ` +
      `(HTTP ${response.status}).`;

    try {
      const errorBody =
        (await response.json()) as {
          detail?: unknown;
        };

      if (
        typeof errorBody.detail ===
        "string"
      ) {
        message =
          errorBody.detail;
      }
    } catch {
      // Keep default HTTP error.
    }

    throw new Error(message);
  }

  return (
    (await response.json()) as
      JiraTicketCreateResponse
  );
}
