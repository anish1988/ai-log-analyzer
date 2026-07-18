"use client";

import { ArrowRight, ChevronDown, RotateCcw } from "lucide-react";
import { useSearchFilters } from "@/hooks/useSearchFilters";
import type { FetchStatus } from "../types";

export interface ActionButtonsProps {
  status: FetchStatus;
  onNext: () => void;
}

export default function ActionButtons({ status, onNext }: ActionButtonsProps) {
  const { reset } = useSearchFilters();
  const isBusy = status === "checking-permission" || status === "fetching";

  return (
    <>
      <div className="mt-6 flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-lg border border-indigo-200 bg-white px-4 py-2.5 text-sm font-medium text-indigo-600 hover:bg-indigo-50"
        >
          + Add filter...
          <ChevronDown className="h-4 w-4" strokeWidth={2} />
        </button>
        <button
          type="button"
          className="rounded-lg bg-indigo-50 px-4 py-2.5 text-sm font-medium text-indigo-600 hover:bg-indigo-100"
        >
          Add
        </button>
      </div>

      <div className="mt-8 flex flex-col-reverse items-stretch justify-end gap-3 border-t border-slate-100 pt-6 sm:flex-row sm:items-center">
        <button
          type="button"
          onClick={reset}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50"
        >
          <RotateCcw className="h-4 w-4" strokeWidth={2} />
          Clear All
        </button>
        <button
          type="button"
          onClick={onNext}
          disabled={isBusy}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {status === "checking-permission"
            ? "Checking permission..."
            : status === "fetching"
            ? "Fetching logs..."
            : "Next"}
          <ArrowRight className="h-4 w-4" strokeWidth={2} />
        </button>
      </div>
    </>
  );
}