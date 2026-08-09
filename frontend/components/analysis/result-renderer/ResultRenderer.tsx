"use client";

import WebResult from "../web-result/WebResult";
import TelephonyResult from "../telephony-result/TelephonyResult";

import type {
    LogFetchResponse,
    WebLogFetchResponse,
} from "@/lib/types/preview";

interface ResultRendererProps {

    tier:string;

    data:
        | LogFetchResponse
        | WebLogFetchResponse;

}

export default function ResultRenderer({
  tier,
  data,
}: ResultRendererProps) {
  switch (tier) {
    case "web":
      return <WebResult data={data} />;

    case "telephony":
      return <TelephonyResult data={data} />;

    default:
      return (
        <div className="rounded-lg border border-dashed p-8 text-center text-gray-500">
          No renderer available for tier <b>{tier}</b>
        </div>
      );
  }
}