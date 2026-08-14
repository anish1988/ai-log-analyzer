"use client";

import WebResult from "../web-result/WebResult";
import TelephonyResult from "../telephony-result/TelephonyResult";

import type {
  AIAnalysisResponse,
} from "@/lib/types/aiAnalysis";

import type {
  LogFetchResponse,
  WebLogFetchResponse,
} from "@/lib/types/preview";

interface ResultRendererProps {
  tier: string;

  data:
    | LogFetchResponse
    | WebLogFetchResponse;

  onBack: () => void;

  onAIAnalysisCompleted?: (
    response: AIAnalysisResponse,
  ) => void;
}

export default function ResultRenderer({
  tier,
  data,
  onBack,
  onAIAnalysisCompleted,
}: ResultRendererProps) {
  switch (tier) {
    case "web":
      return (
        <WebResult
          data={
            data as WebLogFetchResponse
          }
          onBack={onBack}
          onAIAnalysisCompleted={
            onAIAnalysisCompleted
          }
        />
      );

    case "telephony":
      return (
        <TelephonyResult
          data={
            data as LogFetchResponse
          }
          onBack={onBack}
        />
      );

    default:
      return (
        <div className="rounded-lg border border-dashed p-8 text-center text-gray-500">
          No renderer available for tier{" "}
          <b>{tier}</b>
        </div>
      );
  }
}