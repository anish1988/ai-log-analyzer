"use client";

import ChipSelector from "@/components/form/ChipSelector";
import { tierOptions } from "@/config/tier-options";
import { useSearchFilters } from "@/hooks/useSearchFilters";
import type { TierSelection } from "../types";

export default function TierSection() {
  const { filters, setTier } = useSearchFilters();

  return (
    <ChipSelector
      label="Tier"
      options={tierOptions}
      value={filters.tier}
      onChange={(value) => setTier(value as TierSelection)}
    />
  );
}