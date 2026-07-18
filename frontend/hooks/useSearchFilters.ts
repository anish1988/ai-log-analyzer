"use client";

import { useContext } from "react";
import { SearchFiltersContext } from "@/providers/SearchFiltersProvider";

export function useSearchFilters() {
  const ctx = useContext(SearchFiltersContext);
  if (!ctx) {
    throw new Error("useSearchFilters must be used within a <SearchFiltersProvider>");
  }
  return ctx;
}