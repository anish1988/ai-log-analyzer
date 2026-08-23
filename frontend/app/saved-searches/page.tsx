"use client";

import { Bookmark } from "lucide-react";

import {
  SearchFiltersProvider,
} from "@/providers/SearchFiltersProvider";

import SavedSearches from "@/components/search/SavedSearches";

export default function SavedSearchesPage() {
  return (
    <SearchFiltersProvider>

      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* ============================================================ */}
        {/* PAGE HEADER                                                   */}
        {/* ============================================================ */}

        <div className="mb-8">

          <div className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50">

              <Bookmark
                className="h-5 w-5 text-indigo-600"
              />

            </div>

            <div>

              <h1 className="text-2xl font-semibold text-slate-900">
                Saved Searches
              </h1>

              <p className="mt-1 text-sm text-slate-500">
                View and reuse your saved search filters.
              </p>

            </div>

          </div>

        </div>

        {/* ============================================================ */}
        {/* SAVED SEARCHES                                                */}
        {/* ============================================================ */}

        <SavedSearches />

      </div>

    </SearchFiltersProvider>
  );
}