"use client";

import { useCallback, useEffect, useState } from "react";

import { useSearchFilters } from "@/hooks/useSearchFilters";

export interface SavedSearch {
  id: number;
  user_id: string;
  name: string;
  description: string | null;
  from: string;
  to: string;
  tier: "all" | "web" | "db" | "telephony";
  servers: string[];
  searchFilters: {
    leadId?: string;
    campaignId?: string;
    uniqueId?: string;
    callerId?: string;
    callerNumber?: string;
    agent?: string;
    inboundGroup?: string;
    logType?: string | null;
    defaultLogPath?: string | null;
    customLogPath?: string | null;
    [key: string]: unknown;
  };
  created_at: string;
  updated_at: string;
}

interface SavedSearchListResponse {
  items: SavedSearch[];
  total: number;
}

interface UseSavedSearchesResult {
  savedSearches: SavedSearch[];
  total: number;
  isLoading: boolean;
  isLoadingOne: boolean;
  error: string | null;
  loadSavedSearches: () => Promise<void>;
  loadSavedSearch: (
    savedSearchId: number,
  ) => Promise<SavedSearch | null>;
}

export function useSavedSearches(): UseSavedSearchesResult {

  const {
    setField,
    setTier,
  } = useSearchFilters();

  const [
    savedSearches,
    setSavedSearches,
  ] = useState<SavedSearch[]>([]);

  const [
    total,
    setTotal,
  ] = useState(0);

  const [
    isLoading,
    setIsLoading,
  ] = useState(false);

  const [
    isLoadingOne,
    setIsLoadingOne,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(null);

  const apiUrl =
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000";

  const loadSavedSearches = useCallback(
    async () => {

      setIsLoading(true);
      setError(null);

      try {

        const response = await fetch(
          `${apiUrl}/api/saved-searches`,
          {
            method: "GET",
            credentials: "include",
          },
        );

        const data: SavedSearchListResponse =
          await response.json();

        if (!response.ok) {

          throw new Error(
            (
              data as unknown as {
                detail?: string;
              }
            )?.detail ||
            "Failed to load saved searches.",
          );
        }

        setSavedSearches(
          data.items || [],
        );

        setTotal(
          data.total || 0,
        );

      } catch (err) {

        console.error(
          "Failed to load saved searches:",
          err,
        );

        setError(
          err instanceof Error
            ? err.message
            : "Failed to load saved searches.",
        );

        setSavedSearches([]);
        setTotal(0);

      } finally {

        setIsLoading(false);
      }
    },
    [apiUrl],
  );

  const loadSavedSearch = useCallback(
    async (
      savedSearchId: number,
    ): Promise<SavedSearch | null> => {

      setIsLoadingOne(true);
      setError(null);

      try {

        const response = await fetch(
          `${apiUrl}/api/saved-searches/${savedSearchId}`,
          {
            method: "GET",
            credentials: "include",
          },
        );

        const data = await response.json();

        if (!response.ok) {

          throw new Error(
            data?.detail ||
            "Failed to load saved search.",
          );
        }

        const savedSearch =
          data as SavedSearch;

        /*
         * Hydrate the existing SearchFiltersProvider.
         *
         * We deliberately use the existing filter state instead
         * of creating another filter state inside this hook.
         */

        setTier(
          savedSearch.tier,
        );

        setField(
          "from",
          savedSearch.from,
        );

        setField(
          "to",
          savedSearch.to,
        );

        setField(
          "servers",
          savedSearch.servers,
        );

        const filters =
          savedSearch.searchFilters || {};

        setField(
          "leadId",
          String(filters.leadId ?? ""),
        );

        setField(
          "campaignId",
          String(filters.campaignId ?? ""),
        );

        setField(
          "uniqueId",
          String(filters.uniqueId ?? ""),
        );

        setField(
          "callerId",
          String(filters.callerId ?? ""),
        );

        setField(
          "callerNumber",
          String(filters.callerNumber ?? ""),
        );

        setField(
          "agent",
          String(filters.agent ?? ""),
        );

        setField(
          "inboundGroup",
          String(filters.inboundGroup ?? ""),
        );

        setField(
          "logType",
          String(filters.logType ?? ""),
        );

        setField(
          "defaultLogPath",
          String(filters.defaultLogPath ?? ""),
        );

        setField(
          "customLogPath",
          String(filters.customLogPath ?? ""),
        );

        return savedSearch;

      } catch (err) {

        console.error(
          "Failed to load saved search:",
          err,
        );

        setError(
          err instanceof Error
            ? err.message
            : "Failed to load saved search.",
        );

        return null;

      } finally {

        setIsLoadingOne(false);
      }
    },
    [
      apiUrl,
      setField,
      setTier,
    ],
  );

  useEffect(() => {
  const timer = setTimeout(() => {
    void loadSavedSearches();
  }, 0);

  return () => {
    clearTimeout(timer);
  };
 }, [loadSavedSearches]);


  return {
    savedSearches,
    total,
    isLoading,
    isLoadingOne,
    error,
    loadSavedSearches,
    loadSavedSearch,
  };
}