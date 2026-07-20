"use client";

import { Filter } from "lucide-react";
import SectionTitle from "@/components/form/SectionTitle";
import { useSearchFilters } from "@/hooks/useSearchFilters";
import { useLogFetch } from "@/hooks/useLogFetch";

import DateRangeSection from "./components/DateRangeSection";
import TierSection from "./components/TierSection";
import ServerSelection from "./components/ServerSelection";
import SearchFields from "./components/SearchFields";
import ActionButtons from "./components/ActionButtons";

export interface SearchFilterCardProps {
  onNext?: () => void;
}

export default function SearchFilterCard({
  onNext,
}: SearchFilterCardProps) {
  const { filters } = useSearchFilters();
  const { run, status, message, data } = useLogFetch();

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8">
      <SectionTitle icon={<Filter className="h-4 w-4" strokeWidth={2} />}>
        Search Filters
      </SectionTitle>

      {/* Permission Error */}
      {status === "permission-denied" && message && (
        <div className="mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {message}
        </div>
      )}

      {/* Search Form */}
      <div className="space-y-5">
        <DateRangeSection />
        <TierSection />
        <ServerSelection />
        <SearchFields />
      </div>

      {/* Search Button */}
      <ActionButtons
        status={status}
        onNext={() => run(filters)}
      />

      {/* Error */}
      {status === "error" && (
        <div className="mt-6 rounded-lg border border-red-300 bg-red-50 p-4">
          <h3 className="font-semibold text-red-700">
            Error
          </h3>

          <p className="mt-2 text-sm text-red-700">
            {message}
          </p>
        </div>
      )}

      {/* Debug Panel */}
      {status === "success" && data && (
        <div className="mt-8 rounded-xl border border-green-300 bg-green-50 p-5">
          <h2 className="mb-4 text-xl font-bold text-green-700">
            Backend Response (Debug)
          </h2>

          <p>
            <strong>Total Matched Lines:</strong>{" "}
            {data.total_lines}
          </p>

          <p className="mb-4">
            <strong>Total Buckets:</strong>{" "}
            {data.results?.length}
          </p>

          <pre
            className="overflow-auto rounded bg-black p-4 text-xs text-green-400"
            style={{ maxHeight: "450px" }}
          >
            {JSON.stringify(data, null, 2)}
          </pre>

          <div className="mt-6 flex justify-end">
            <button
              onClick={() => onNext?.()}
              className="rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700"
            >
              Continue to Step 2 →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}