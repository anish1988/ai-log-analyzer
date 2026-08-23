"use client";

import {
  Bookmark,
  Check,
  Edit3,
  Loader2,
  Search,
  Trash2,
  X,
} from "lucide-react";

import { useState } from "react";

import { useRouter } from "next/navigation";

import {
  SavedSearch,
  useSavedSearches,
} from "@/hooks/useSavedSearches";

interface SavedSearchesProps {
  onLoaded?: (savedSearch: SavedSearch) => void;
}

export default function SavedSearches({
  onLoaded,
}: SavedSearchesProps) {

  const router = useRouter();


  const {
    savedSearches,
    total,
    isLoading,
    isLoadingOne,
    error,
    loadSavedSearch,
    loadSavedSearches,
  } = useSavedSearches();

  const [
    selectedId,
    setSelectedId,
  ] = useState<number | null>(null);

  const [
    editingSearch,
    setEditingSearch,
  ] = useState<SavedSearch | null>(null);

  const [
    editName,
    setEditName,
  ] = useState("");

  const [
    editDescription,
    setEditDescription,
  ] = useState("");

  const [
    isUpdating,
    setIsUpdating,
  ] = useState(false);

  const [
    deletingId,
    setDeletingId,
  ] = useState<number | null>(null);

  const [
    actionError,
    setActionError,
  ] = useState<string | null>(null);

  const [
    actionMessage,
    setActionMessage,
  ] = useState<string | null>(null);

  const apiUrl =
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000";


  const handleLoad = async (
  savedSearchId: number,
) => {

  setSelectedId(savedSearchId);
  setActionError(null);
  setActionMessage(null);

  try {

    /*
     * Verify that the saved search belongs to the
     * current user before navigating.
     *
     * The backend performs the actual ownership check.
     */

    const savedSearch =
      await loadSavedSearch(
        savedSearchId,
      );

    if (!savedSearch) {
      return;
    }

    onLoaded?.(savedSearch);

    /*
     * Pass only the saved-search ID to New Analysis.
     *
     * New Analysis will fetch the record again and
     * hydrate its own SearchFiltersProvider.
     *
     * We deliberately do NOT pass filter values
     * through the URL.
     */

    router.push(
      `/new-analysis?savedSearchId=${savedSearch.id}`,
    );

  } finally {

    setSelectedId(null);
  }
};

  const handleEditOpen = (
    savedSearch: SavedSearch,
  ) => {

    setEditingSearch(
      savedSearch,
    );

    setEditName(
      savedSearch.name,
    );

    setEditDescription(
      savedSearch.description || "",
    );

    setActionError(null);
    setActionMessage(null);
  };

  const handleEditCancel = () => {

    if (isUpdating) {
      return;
    }

    setEditingSearch(null);
    setEditName("");
    setEditDescription("");
  };

  const handleEditSave = async () => {

    if (!editingSearch) {
      return;
    }

    const trimmedName =
      editName.trim();

    if (!trimmedName) {

      setActionError(
        "Search name is required.",
      );

      return;
    }

    setIsUpdating(true);
    setActionError(null);
    setActionMessage(null);

    try {

      const response = await fetch(
        `${apiUrl}/api/saved-searches/${editingSearch.id}`,
        {
          method: "PUT",

          headers: {
            "Content-Type": "application/json",
          },

          credentials: "include",

          body: JSON.stringify({
            name: trimmedName,

            description:
              editDescription.trim() ||
              null,

            from: editingSearch.from,

            to: editingSearch.to,

            tier: editingSearch.tier,

            servers: editingSearch.servers,

            searchFilters:
              editingSearch.searchFilters,
          }),
        },
      );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data?.detail ||
          "Failed to update saved search.",
        );
      }

      setEditingSearch(null);
      setEditName("");
      setEditDescription("");

      setActionMessage(
        "Saved search updated successfully.",
      );

      await loadSavedSearches();

    } catch (err) {

      console.error(
        "Failed to update saved search:",
        err,
      );

      setActionError(
        err instanceof Error
          ? err.message
          : "Failed to update saved search.",
      );

    } finally {

      setIsUpdating(false);
    }
  };

  const handleDelete = async (
    savedSearch: SavedSearch,
  ) => {

    const confirmed =
      window.confirm(
        `Are you sure you want to delete "${savedSearch.name}"?`,
      );

    if (!confirmed) {
      return;
    }

    setDeletingId(
      savedSearch.id,
    );

    setActionError(null);
    setActionMessage(null);

    try {

      const response = await fetch(
        `${apiUrl}/api/saved-searches/${savedSearch.id}`,
        {
          method: "DELETE",
          credentials: "include",
        },
      );

      if (!response.ok) {

        const data =
          await response.json();

        throw new Error(
          data?.detail ||
          "Failed to delete saved search.",
        );
      }

      setActionMessage(
        `"${savedSearch.name}" deleted successfully.`,
      );

      await loadSavedSearches();

    } catch (err) {

      console.error(
        "Failed to delete saved search:",
        err,
      );

      setActionError(
        err instanceof Error
          ? err.message
          : "Failed to delete saved search.",
      );

    } finally {

      setDeletingId(null);
    }
  };

  if (
    isLoading &&
    savedSearches.length === 0
  ) {

    return (
      <section className="rounded-xl border border-slate-200 bg-white">

        <div className="flex items-center gap-2 px-5 py-8 text-sm text-slate-500">

          <Loader2
            className="h-4 w-4 animate-spin"
          />

          Loading saved searches...

        </div>

      </section>
    );
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white">

      {/* ================================================================ */}
      {/* HEADER                                                           */}
      {/* ================================================================ */}

      <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">

        <div>

          <div className="flex items-center gap-2">

            <Bookmark
              className="h-5 w-5 text-indigo-600"
            />

            <h2 className="text-base font-semibold text-slate-900">
              Saved Searches
            </h2>

          </div>

          <p className="mt-1 text-xs text-slate-500">
            {total}{" "}
            {total === 1
              ? "saved search"
              : "saved searches"}
          </p>

        </div>

        <Search
          className="h-5 w-5 text-slate-400"
        />

      </div>

      {/* ================================================================ */}
      {/* ACTION MESSAGE                                                   */}
      {/* ================================================================ */}

      {actionMessage && (

        <div className="mx-5 mt-4 rounded-lg border border-green-200 bg-green-50 px-3 py-2.5 text-sm text-green-700">

          <div className="flex items-center gap-2">

            <Check className="h-4 w-4" />

            {actionMessage}

          </div>

        </div>
      )}

      {/* ================================================================ */}
      {/* ERROR                                                            */}
      {/* ================================================================ */}

      {(error || actionError) && (

        <div className="mx-5 mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">

          {actionError || error}

        </div>
      )}

      {/* ================================================================ */}
      {/* EMPTY                                                            */}
      {/* ================================================================ */}

      {!isLoading &&
        savedSearches.length === 0 &&
        !error && (

          <div className="px-5 py-12 text-center">

            <Bookmark
              className="mx-auto h-9 w-9 text-slate-300"
            />

            <p className="mt-3 text-sm font-medium text-slate-600">
              No saved searches
            </p>

            <p className="mt-1 text-xs text-slate-400">
              Save your current filters from the New Analysis page.
            </p>

          </div>
        )}

      {/* ================================================================ */}
      {/* TABLE                                                            */}
      {/* ================================================================ */}

      {savedSearches.length > 0 && (

        <div className="overflow-x-auto">

          <table className="w-full min-w-[850px]">

            <thead>

              <tr className="border-b border-slate-100 bg-slate-50">

                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Name
                </th>

                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Tier
                </th>

                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Date Range
                </th>

                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Created
                </th>

                <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Actions
                </th>

              </tr>

            </thead>

            <tbody className="divide-y divide-slate-100">

              {savedSearches.map(
                (savedSearch) => (

                  <tr
                    key={savedSearch.id}
                    className="hover:bg-slate-50"
                  >

                    {/* NAME */}

                    <td className="px-5 py-4">

                      <div className="max-w-xs">

                        <p className="truncate text-sm font-medium text-slate-800">
                          {savedSearch.name}
                        </p>

                        {savedSearch.description && (

                          <p className="mt-1 truncate text-xs text-slate-500">
                            {savedSearch.description}
                          </p>

                        )}

                      </div>

                    </td>

                    {/* TIER */}

                    <td className="px-5 py-4">

                      <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium capitalize text-slate-600">
                        {savedSearch.tier}
                      </span>

                    </td>

                    {/* DATE */}

                    <td className="px-5 py-4">

                      <div className="flex items-center gap-1.5 text-sm text-slate-600">

                        <span>
                          {savedSearch.from}
                        </span>

                        <span className="text-slate-400">
                          →
                        </span>

                        <span>
                          {savedSearch.to}
                        </span>

                      </div>

                    </td>

                    {/* CREATED */}

                    <td className="px-5 py-4">

                      <span className="text-sm text-slate-500">

                        {new Date(
                          savedSearch.created_at,
                        ).toLocaleDateString()}

                      </span>

                    </td>

                    {/* ACTIONS */}

                    <td className="px-5 py-4">

                      <div className="flex items-center justify-end gap-2">

                        {/* LOAD */}

                        <button
                          type="button"
                          onClick={() =>
                            handleLoad(
                              savedSearch.id,
                            )
                          }
                          disabled={
                            isLoadingOne &&
                            selectedId ===
                              savedSearch.id
                          }
                          className="inline-flex items-center gap-1.5 rounded-lg border border-indigo-200 bg-white px-3 py-2 text-xs font-medium text-indigo-600 hover:bg-indigo-50 disabled:cursor-not-allowed disabled:opacity-60"
                        >

                          {isLoadingOne &&
                          selectedId ===
                            savedSearch.id ? (

                            <Loader2
                              className="h-3.5 w-3.5 animate-spin"
                            />

                          ) : (

                            <Search
                              className="h-3.5 w-3.5"
                            />

                          )}

                          Load

                        </button>

                        {/* EDIT */}

                        <button
                          type="button"
                          onClick={() =>
                            handleEditOpen(
                              savedSearch,
                            )
                          }
                          disabled={
                            isUpdating ||
                            deletingId !== null
                          }
                          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                        >

                          <Edit3
                            className="h-3.5 w-3.5"
                          />

                          Edit

                        </button>

                        {/* DELETE */}

                        <button
                          type="button"
                          onClick={() =>
                            handleDelete(
                              savedSearch,
                            )
                          }
                          disabled={
                            deletingId !== null ||
                            isUpdating
                          }
                          className="inline-flex items-center gap-1.5 rounded-lg border border-red-200 bg-white px-3 py-2 text-xs font-medium text-red-600 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60"
                        >

                          {deletingId ===
                          savedSearch.id ? (

                            <Loader2
                              className="h-3.5 w-3.5 animate-spin"
                            />

                          ) : (

                            <Trash2
                              className="h-3.5 w-3.5"
                            />

                          )}

                          Delete

                        </button>

                      </div>

                    </td>

                  </tr>
                ),
              )}

            </tbody>

          </table>

        </div>
      )}

      {/* ================================================================ */}
      {/* EDIT MODAL                                                       */}
      {/* ================================================================ */}

      {editingSearch && (

        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="edit-saved-search-title"
        >

          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">

            <div className="mb-5 flex items-start justify-between">

              <div>

                <h2
                  id="edit-saved-search-title"
                  className="text-lg font-semibold text-slate-900"
                >
                  Edit Saved Search
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Update the saved search name or description.
                </p>

              </div>

              <button
                type="button"
                onClick={handleEditCancel}
                disabled={isUpdating}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 disabled:opacity-50"
              >

                <X className="h-5 w-5" />

              </button>

            </div>

            {/* NAME */}

            <div className="mb-4">

              <label
                htmlFor="edit-saved-search-name"
                className="mb-1.5 block text-sm font-medium text-slate-700"
              >
                Search Name
              </label>

              <input
                id="edit-saved-search-name"
                type="text"
                value={editName}
                onChange={(event) =>
                  setEditName(
                    event.target.value,
                  )
                }
                maxLength={255}
                disabled={isUpdating}
                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:bg-slate-100"
              />

            </div>

            {/* DESCRIPTION */}

            <div className="mb-5">

              <label
                htmlFor="edit-saved-search-description"
                className="mb-1.5 block text-sm font-medium text-slate-700"
              >
                Description
              </label>

              <textarea
                id="edit-saved-search-description"
                value={editDescription}
                onChange={(event) =>
                  setEditDescription(
                    event.target.value,
                  )
                }
                maxLength={2000}
                rows={4}
                disabled={isUpdating}
                className="w-full resize-none rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:bg-slate-100"
              />

            </div>

            {/* MODAL ACTIONS */}

            <div className="flex justify-end gap-3">

              <button
                type="button"
                onClick={handleEditCancel}
                disabled={isUpdating}
                className="rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={handleEditSave}
                disabled={
                  isUpdating ||
                  !editName.trim()
                }
                className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
              >

                {isUpdating && (

                  <Loader2
                    className="h-4 w-4 animate-spin"
                  />

                )}

                {isUpdating
                  ? "Updating..."
                  : "Update"}

              </button>

            </div>

          </div>

        </div>
      )}

    </section>
  );
}