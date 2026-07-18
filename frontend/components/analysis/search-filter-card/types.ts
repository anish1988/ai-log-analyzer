/**
 * Component-local types for the search-filter-card.
 * Shared, cross-app state/response shapes live in @/types/log-analysis
 * (the backend owns anything with real IPs/SSH details — this file only
 * re-exports what the card's subcomponents actually need).
 */
export type { SearchFiltersState, Tier, TierSelection } from "@/types/log-analysis";

export type FetchStatus =
  | "idle"
  | "checking-permission"
  | "permission-denied"
  | "fetching"
  | "success"
  | "error";