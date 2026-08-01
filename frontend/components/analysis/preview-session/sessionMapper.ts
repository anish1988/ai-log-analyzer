import type { LogFetchResponse } from "@/lib/log-analysis/types";
import type { Session } from "./SessionList";

export function mapLogFetchResponseToSessions(
  response: LogFetchResponse
): Session[] {

  if (!response) {
    return [];
  }

  // Replace "results" with your actual property name
  return response.results.map((item, index) => ({
    id: item.session_id ?? `SESSION-${index + 1}`,

    leadId: item.lead_id ?? "-",

    campaign: item.campaign_id ?? "-",

    duration: `${item.start_time ?? "-"} - ${item.end_time ?? "-"}`,

    servers: item.servers ?? [],

    totalLines: item.total_lines ?? 0,

    summary: item.summary ?? "No summary available",

    errors: item.error_count ?? 0,

    warnings: item.warning_count ?? 0,
  }));
}