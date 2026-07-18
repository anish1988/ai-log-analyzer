"use client";

import DateField from "@/components/form/DateField";
import { useSearchFilters } from "@/hooks/useSearchFilters";

export default function DateRangeSection() {
  const { filters, setField } = useSearchFilters();

  return (
    <div className="grid grid-cols-1 gap-x-6 gap-y-5 sm:grid-cols-2">
      <DateField
        label="From"
        required
        value={filters.from}
        onChange={(e) => setField("from", e.target.value)}
      />
      <DateField
        label="To"
        required
        value={filters.to}
        onChange={(e) => setField("to", e.target.value)}
      />
    </div>
  );
}