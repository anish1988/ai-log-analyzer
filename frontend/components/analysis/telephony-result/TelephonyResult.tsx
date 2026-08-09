"use client";

import type { LogFetchResponse }
from "@/lib/types/preview";

interface Props{

    data:LogFetchResponse;

}

export default function TelephonyResult({ data }: Props) {
  return (
    <div className="rounded-lg border bg-white p-6">
      <h2 className="text-xl font-semibold">
        Telephony Result
      </h2>

      <pre className="mt-4 overflow-auto text-sm">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}