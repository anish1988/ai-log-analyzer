"use client";

import { useCallback, useReducer } from "react";
import { useRouter } from "next/navigation";
import type {
  LogFetchResponse,
  PermissionCheckResponse,
  SearchFiltersState,
} from "@/lib/log-analysis/types";

const API = process.env.NEXT_PUBLIC_API_URL;
type Status =
  | "idle"
  | "checking-permission"
  | "permission-denied"
  | "fetching"
  | "success"
  | "error";

interface State {
  status: Status;
  message: string | null;
  data: LogFetchResponse | null;
}

type Action =
  | { type: "START_PERMISSION_CHECK" }
  | { type: "PERMISSION_DENIED"; message: string }
  | { type: "START_FETCH" }
  | { type: "FETCH_SUCCESS"; data: LogFetchResponse }
  | { type: "FETCH_ERROR"; message: string }
  | { type: "RESET" };

const initialState: State = { status: "idle", message: null, data: null };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "START_PERMISSION_CHECK":
      return { status: "checking-permission", message: null, data: null };
    case "PERMISSION_DENIED":
      return { status: "permission-denied", message: action.message, data: null };
    case "START_FETCH":
      return { status: "fetching", message: null, data: null };
    case "FETCH_SUCCESS":
      return { status: "success", message: null, data: action.data };
    case "FETCH_ERROR":
      return { status: "error", message: action.message, data: null };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

export function useLogFetch() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const router = useRouter();

  const run = useCallback(
    async (filters: SearchFiltersState) => {
      dispatch({ type: "START_PERMISSION_CHECK" });

      const permissionRes = await fetch(`${API}/api/logs/permission`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tier: filters.tier, servers: filters.servers }),
      });
      const permission: PermissionCheckResponse = await permissionRes.json();

      if (!permissionRes.ok || !permission.granted) {
        const message = permission?.message ?? "Permission is required to access the selected servers.";
        dispatch({ type: "PERMISSION_DENIED", message });
        router.push(`/new-analysis?step=1&error=${encodeURIComponent(message)}`);
        return;
      }

      dispatch({ type: "START_FETCH" });
      try {
        const fetchRes = await fetch(`${API}/api/logs/fetch`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(filters),
        });

        if (!fetchRes.ok) {
          const err = await fetchRes.json().catch(() => null);
          throw new Error(err?.message ?? "Failed to fetch logs.");
        }

        const data: LogFetchResponse = await fetchRes.json();
        dispatch({ type: "FETCH_SUCCESS", data });
      } catch (err) {
        dispatch({
          type: "FETCH_ERROR",
          message: err instanceof Error ? err.message : "Unknown error while fetching logs.",
        });
      }
    },
    [router]
  );

  const reset = useCallback(() => dispatch({ type: "RESET" }), []);

  return { ...state, run, reset };
}