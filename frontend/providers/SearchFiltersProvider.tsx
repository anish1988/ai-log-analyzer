"use client";

import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useReducer,
  type ReactNode,
} from "react";
import type { SearchFiltersState } from "@/types/log-analysis";

const STORAGE_KEY = "log-analysis:search-filters";

const initialState: SearchFiltersState = {
  from: "",
  to: "",
  tier: "all",
  servers: [],
  leadId: "",
  campaignId: "",
  uniqueId: "",
  callerId: "",
  callerNumber: "",
  agent: "",
  inboundGroup: "",
};

type Action =
  | { type: "SET_FIELD"; key: keyof SearchFiltersState; value: SearchFiltersState[keyof SearchFiltersState] }
  | { type: "SET_TIER"; tier: SearchFiltersState["tier"] }
  | { type: "RESET" }
  | { type: "HYDRATE"; state: SearchFiltersState };

function reducer(state: SearchFiltersState, action: Action): SearchFiltersState {
  switch (action.type) {
    case "SET_FIELD":
      return { ...state, [action.key]: action.value };
    case "SET_TIER":
      return { ...state, tier: action.tier, servers: [] };
    case "RESET":
      return initialState;
    case "HYDRATE":
      return action.state;
    default:
      return state;
  }
}

export interface SearchFiltersContextValue {
  filters: SearchFiltersState;
  setField: <K extends keyof SearchFiltersState>(key: K, value: SearchFiltersState[K]) => void;
  setTier: (tier: SearchFiltersState["tier"]) => void;
  reset: () => void;
  isValid: boolean;
}

export const SearchFiltersContext = createContext<SearchFiltersContextValue | null>(null);

export function SearchFiltersProvider({ children }: { children: ReactNode }) {
  const [filters, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    try {
      dispatch({ type: "HYDRATE", state: JSON.parse(raw) });
    } catch {
      // Corrupt or outdated shape in storage - ignore and keep defaults.
    }
  }, []);

  useEffect(() => {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(filters));
  }, [filters]);

  const setField = useCallback(
    <K extends keyof SearchFiltersState>(key: K, value: SearchFiltersState[K]) => {
      dispatch({ type: "SET_FIELD", key, value });
    },
    []
  );

  const setTier = useCallback((tier: SearchFiltersState["tier"]) => {
    dispatch({ type: "SET_TIER", tier });
  }, []);

  const reset = useCallback(() => {
    sessionStorage.removeItem(STORAGE_KEY);
    dispatch({ type: "RESET" });
  }, []);

  const isValid = useMemo(() => {
    const hasSearchTerm = [
      filters.leadId,
      filters.campaignId,
      filters.uniqueId,
      filters.callerId,
      filters.callerNumber,
      filters.agent,
      filters.inboundGroup,
    ].some((value) => value.trim().length > 0);

    return Boolean(filters.from && filters.to && filters.servers.length > 0 && hasSearchTerm);
  }, [filters]);

  const value = useMemo(
    () => ({ filters, setField, setTier, reset, isValid }),
    [filters, setField, setTier, reset, isValid]
  );

  return (
    <SearchFiltersContext.Provider value={value}>{children}</SearchFiltersContext.Provider>
  );
}