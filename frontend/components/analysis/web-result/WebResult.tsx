"use client";

interface Props {
  data: WebLogFetchResponse;
  onBack: () => void;
  onAnalyzeSelected?: (errorIds: string[]) => void;
}

import { useMemo, useState } from "react";
import type {
  
  WebLogFetchResponse,
} from "@/lib/types/preview";
import ErrorTree from "./ErrorTree";
import ErrorDetails from "./ErrorDetails";
import LogLineTable from "./LogLineTable";
import WizardNavigation from "@/components/analysis/shared/WizardNavigation";

export default function WebResult({ data, onBack, onAnalyzeSelected, }: Props) {

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
        const [selectedErrorIds, setSelectedErrorIds] = useState<string[]>([]);
        const toggleErrorSelection = (errorId: string) => {

        setSelectedErrorIds(previous => {
            if (previous.includes(errorId)) {
                return previous.filter(id => id !== errorId);
            }
            return [...previous, errorId];
        });
        };

        const selectAllErrors = () => {

            setSelectedErrorIds(

                allErrors.map(error => error.error_id)

            );

        };

        const clearSelectedErrors = () => {

            setSelectedErrorIds([]);

        };

        const selectedError = allErrors.find(
        e => e.error_id === selectedErrorId
        );

        const handleAnalyzeSelected = () => {

        const selectedErrors = allErrors.filter(error =>
            selectedErrorIds.includes(error.error_id)
        );

        console.log("====================================");
        console.log("SELECTED ERRORS FOR AI ANALYSIS");
        console.log("====================================");
        console.log(selectedErrors);
        console.log("====================================");

        onAnalyzeSelected?.(selectedErrorIds);

    };
        
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
       <WizardNavigation
            onBack={onBack}
            onNext={handleAnalyzeSelected}
            nextLabel="Analyze Selected"
            selectedCount={selectedErrorIds.length}
            disableNext={selectedErrorIds.length === 0}
        />

      {/* Main Layout */}
     
      <div className="grid grid-cols-12 gap-6">

        {/* Left Panel */}
                <div className="col-span-3">
                 <ErrorTree
                    errors={allErrors}
                    selectedErrorId={selectedErrorId}
                    onSelect={setSelectedErrorId}
                    selectedErrorIds={selectedErrorIds}
                    onToggleSelection={toggleErrorSelection}
                    onSelectAll={selectAllErrors}
                    onClearSelection={clearSelectedErrors}
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
            {/* Wizard Navigation */}

            <WizardNavigation

                onBack={onBack}

                onNext={handleAnalyzeSelected}

                nextLabel="Analyze Selected"

                selectedCount={selectedErrorIds.length}

                disableNext={selectedErrorIds.length === 0}

            />

      <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-sm">

        <button
          onClick={onBack}
          className="rounded-lg border border-slate-300 px-5 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
        >
          ← Back
        </button>

        <div className="flex items-center gap-4">
            <span className="text-sm text-slate-500">
                Selected:
                <span className="ml-1 font-semibold text-indigo-600">
                    {selectedErrorIds.length}
                </span>
                {" "}Error{selectedErrorIds.length !== 1 ? "s" : ""}
            </span>

            <button
                disabled={selectedErrorIds.length === 0}
                onClick={() =>
                    onAnalyzeSelected?.(selectedErrorIds)
                }
                className={`rounded-lg px-6 py-2 text-sm font-semibold text-white transition
                ${
                    selectedErrorIds.length === 0
                        ? "cursor-not-allowed bg-indigo-300"
                        : "bg-indigo-600 hover:bg-indigo-700"
                }`}            >
                Analyze Selected
                {selectedErrorIds.length > 0 &&
                    ` (${selectedErrorIds.length})`}  {" →"}
            </button>

        </div>

      </div>

    </div>
  );
}