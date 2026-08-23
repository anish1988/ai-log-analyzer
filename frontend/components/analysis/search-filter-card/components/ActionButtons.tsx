"use client";

import {
  ArrowRight,
  ChevronDown,
  RotateCcw,
  Save,
} from "lucide-react";

import { useState } from "react";

import { useSearchFilters } from "@/hooks/useSearchFilters";

import type { FetchStatus } from "../types";

export interface ActionButtonsProps {
  status: FetchStatus;
  onNext: () => void;
}

export default function ActionButtons({
  status,
  onNext,
}: ActionButtonsProps) {

  const { filters, reset } = useSearchFilters();

  const [
    isSaveDialogOpen,
    setIsSaveDialogOpen,
  ] = useState(false);

  const [
    saveName,
    setSaveName,
  ] = useState("");

  const [
    saveDescription,
    setSaveDescription,
  ] = useState("");

  const [
    isSaving,
    setIsSaving,
  ] = useState(false);

  const [
    saveMessage,
    setSaveMessage,
  ] = useState<string | null>(null);

  const [
    saveError,
    setSaveError,
  ] = useState<string | null>(null);

  const isBusy =
    status === "checking-permission" ||
    status === "fetching";

  const openSaveDialog = () => {
    setSaveName("");
    setSaveDescription("");
    setSaveMessage(null);
    setSaveError(null);
    setIsSaveDialogOpen(true);
  };

  const closeSaveDialog = () => {

    if (isSaving) {
      return;
    }

    setIsSaveDialogOpen(false);
  };

  const handleSaveSearch = async () => {

    const trimmedName = saveName.trim();

    if (!trimmedName) {
      setSaveError(
        "Please enter a name for the saved search.",
      );
      return;
    }

    setIsSaving(true);
    setSaveError(null);
    setSaveMessage(null);

    try {

      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL ||
        "http://localhost:8000";

      const response = await fetch(
        `${apiUrl}/api/saved-searches`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          credentials: "include",

          body: JSON.stringify({
            name: trimmedName,

            description:
              saveDescription.trim() || null,

            from: filters.from ? filters.from.slice(0, 10) : null,

            to: filters.to ? filters.from.slice(0, 10): null,

            tier: filters.tier,

            servers: filters.servers,

            searchFilters: {
              leadId: filters.leadId,
              campaignId: filters.campaignId,
              uniqueId: filters.uniqueId,
              callerId: filters.callerId,
              callerNumber: filters.callerNumber,
              agent: filters.agent,
              inboundGroup: filters.inboundGroup,
              logType: filters.logType,
              defaultLogPath:
                filters.defaultLogPath,
              customLogPath:
                filters.customLogPath,
            },
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {

        throw new Error(
          data?.detail ||
          "Failed to save search.",
        );
      }

      setSaveMessage(
        "Search saved successfully.",
      );

      setTimeout(() => {
        setIsSaveDialogOpen(false);
      }, 700);

    } catch (error) {

      console.error(
        "Failed to save search:",
        error,
      );

      setSaveError(
        error instanceof Error
          ? error.message
          : "Failed to save search.",
      );

    } finally {

      setIsSaving(false);
    }
  };

  return (
    <>
      {/* ================================================================ */}
      {/* FILTER ACTIONS                                                  */}
      {/* ================================================================ */}

      <div className="mt-6 flex flex-wrap items-center gap-3">

        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-lg border border-indigo-200 bg-white px-4 py-2.5 text-sm font-medium text-indigo-600 hover:bg-indigo-50"
        >
          + Add filter...
          <ChevronDown
            className="h-4 w-4"
            strokeWidth={2}
          />
        </button>

        <button
          type="button"
          className="rounded-lg bg-indigo-50 px-4 py-2.5 text-sm font-medium text-indigo-600 hover:bg-indigo-100"
        >
          Add
        </button>

      </div>

      {/* ================================================================ */}
      {/* MAIN ACTIONS                                                     */}
      {/* ================================================================ */}

      <div className="mt-8 flex flex-col-reverse items-stretch justify-end gap-3 border-t border-slate-100 pt-6 sm:flex-row sm:items-center">

        {/* CLEAR */}

        <button
          type="button"
          onClick={reset}
          disabled={isBusy || isSaving}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <RotateCcw
            className="h-4 w-4"
            strokeWidth={2}
          />

          Clear All
        </button>

        {/* SAVE SEARCH */}

        <button
          type="button"
          onClick={openSaveDialog}
          disabled={isBusy || isSaving}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-indigo-200 bg-white px-5 py-2.5 text-sm font-medium text-indigo-600 hover:bg-indigo-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <Save
            className="h-4 w-4"
            strokeWidth={2}
          />

          Save Search
        </button>

        {/* NEXT */}

        <button
          type="button"
          onClick={onNext}
          disabled={isBusy || isSaving}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
        >

          {status === "checking-permission"
            ? "Checking permission..."
            : status === "fetching"
            ? "Fetching logs..."
            : "Next"}

          <ArrowRight
            className="h-4 w-4"
            strokeWidth={2}
          />

        </button>

      </div>

      {/* ================================================================ */}
      {/* SAVE SEARCH DIALOG                                               */}
      {/* ================================================================ */}

      {isSaveDialogOpen && (

        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="save-search-title"
        >

          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">

            <div className="mb-5">

              <h2
                id="save-search-title"
                className="text-lg font-semibold text-slate-900"
              >
                Save Search
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Save the current search filters for later use.
              </p>

            </div>

            {/* NAME */}

            <div className="mb-4">

              <label
                htmlFor="saved-search-name"
                className="mb-1.5 block text-sm font-medium text-slate-700"
              >
                Search Name
              </label>

              <input
                id="saved-search-name"
                type="text"
                value={saveName}
                onChange={(event) =>
                  setSaveName(event.target.value)
                }
                placeholder="e.g. My Lead Search"
                maxLength={255}
                autoFocus
                disabled={isSaving}
                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:bg-slate-100"
              />

            </div>

            {/* DESCRIPTION */}

            <div className="mb-4">

              <label
                htmlFor="saved-search-description"
                className="mb-1.5 block text-sm font-medium text-slate-700"
              >
                Description
                <span className="ml-1 font-normal text-slate-400">
                  (optional)
                </span>
              </label>

              <textarea
                id="saved-search-description"
                value={saveDescription}
                onChange={(event) =>
                  setSaveDescription(event.target.value)
                }
                placeholder="Optional description"
                maxLength={2000}
                rows={3}
                disabled={isSaving}
                className="w-full resize-none rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:bg-slate-100"
              />

            </div>

            {/* ERROR */}

            {saveError && (

              <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
                {saveError}
              </div>

            )}

            {/* SUCCESS */}

            {saveMessage && (

              <div className="mb-4 rounded-lg border border-green-200 bg-green-50 px-3 py-2.5 text-sm text-green-700">
                {saveMessage}
              </div>

            )}

            {/* ACTIONS */}

            <div className="flex justify-end gap-3">

              <button
                type="button"
                onClick={closeSaveDialog}
                disabled={isSaving}
                className="rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={handleSaveSearch}
                disabled={isSaving}
                className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isSaving
                  ? "Saving..."
                  : "Save Search"}
              </button>

            </div>

          </div>

        </div>

      )}

    </>
  );
}