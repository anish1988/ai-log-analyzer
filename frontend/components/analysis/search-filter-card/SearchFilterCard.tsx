"use client";

import { useEffect } from "react";
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
  /** Called once the permission check + log fetch both succeed. */
  onNext?: () => void;
}

export default function SearchFilterCard({ onNext }: SearchFilterCardProps) {
  const { filters } = useSearchFilters();
  const { run, status, message } = useLogFetch();

  // Advance the wizard only once the hook actually reaches "success" -
  // watching status (not the return value of run()) avoids acting on a
  // stale closure.
  useEffect(() => {
    if (status === "success") {
      onNext?.();
    }
  }, [status, onNext]);

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8">
      <SectionTitle icon={<Filter className="h-4 w-4" strokeWidth={2} />}>
        Search filters
      </SectionTitle>

      {status === "permission-denied" && message && (
        <div className="mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {message}
        </div>
      )}

      <div className="space-y-5">
        <DateRangeSection />
        <TierSection />
        <ServerSelection />
        <SearchFields />
      </div>

      <ActionButtons status={status} onNext={() => run(filters)} />
    </div>
  );
}