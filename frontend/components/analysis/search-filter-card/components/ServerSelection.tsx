"use client";

import { useMemo } from "react";
import MultiSelect from "@/components/form/MultiSelect";
import { getServerOptionsForTier } from "@/config/server-options";
import { useSearchFilters } from "@/hooks/useSearchFilters";

export default function ServerSelection() {
  const { filters, setField } = useSearchFilters();

  // Point 3/4: "All" offers every server; a single tier restricts the
  // options to that tier's servers only.
  const serverOptions = useMemo(
    () => getServerOptionsForTier(filters.tier),
    [filters.tier]
  );

  return (
    <MultiSelect
      label="Server / cluster / IP (multi-select)"
      placeholder="Select servers..."
      options={serverOptions}
      value={filters.servers}
      onChange={(value) => setField("servers", value)}
    />
  );
}