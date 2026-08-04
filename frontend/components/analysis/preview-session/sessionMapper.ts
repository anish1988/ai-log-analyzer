import type { LogFetchResponse } from "@/lib/log-analysis/types";

export function mapLogFetchResponseToSessions(
  response: LogFetchResponse
) {
  if (!response) {
    return [];
  }

  console.log("=================================");
  console.log("mapLogFetchResponseToSessions()");
  console.log(response);
  console.log("=================================");

  return response.results.map((item, index) => {
    //----------------------------------------------------------
    // Dynamic fields (Lead ID, Campaign, Agent, etc.)
    //----------------------------------------------------------
    const fields: {
      label: string;
      value: string;
    }[] = [];

    Object.entries(item.meta ?? {}).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        fields.push({
          label: key,
          value: String(value),
        });
      }
    });

    //----------------------------------------------------------
    // Statistics
    //----------------------------------------------------------
    const stats = [
      {
        label: "Matched Lines",
        value: item.matched_count,
      },
    ];

    //----------------------------------------------------------
    // Final object for UI
    //----------------------------------------------------------
    const finalResponse = {
      id: item.file_id || `FILE-${index + 1}`,

      title: item.file_label,

      server: item.server,

      searchedFile: item.searched_file,

      matchedCount: item.matched_count,

      fields,

      stats,

      lines: item.lines,

      raw: item,
    };

    console.log("Mapped Response");
    console.log(finalResponse);

    return finalResponse;
  });
}