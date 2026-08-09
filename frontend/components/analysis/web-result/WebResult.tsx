"use client";

interface Props {
  data: WebLogFetchResponse;
}

import { useMemo, useState } from "react";
import type {
  
  WebLogFetchResponse,
} from "@/lib/types/preview";
import ErrorTree from "./ErrorTree";
import ErrorDetails from "./ErrorDetails";
import LogLineTable from "./LogLineTable";

export default function WebResult({ data }: Props) {

    const allErrors = useMemo(() => {

        return data.results.flatMap(file =>
            file.errors.map(error => ({
            ...error,
            file_name: file.file_name,
            server: file.server,
            }))
        );

        }, [data]);

        const [selectedErrorId, setSelectedErrorId] = useState(
        allErrors[0]?.error_id
        );
       

        const selectedError = allErrors.find(
        e => e.error_id === selectedErrorId
        );
        
  return (
    <div className="space-y-6">

      {/* Page Header */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-slate-800">
          Web Log Analysis
        </h1>

        <p className="mt-2 text-sm text-slate-500">
            {data.results[0].file_name}
                •
                {data.results[0].total_errors}
                Errors Found
        </p>
      </div>

      {/* Main Layout */}
      <div className="grid grid-cols-12 gap-6">

        {/* Left Panel */}
                <div className="col-span-3">
                 <ErrorTree
                    errors={allErrors}
                    selectedErrorId={selectedErrorId}
                    onSelect={setSelectedErrorId}
                 />
        </div>

        {/* Right Panel */}
        <div className="col-span-9 space-y-6">

          {/* Error Summary */}
          <ErrorDetails
                 error={selectedError}
            />

          {/* Log Table */}
          <LogLineTable
               lines={selectedError?.lines ?? []}
          />

        </div>

      </div>

    </div>
  );
}