"use client";

import { ArrowLeft, ArrowRight, RotateCcw } from "lucide-react";

interface PreviewFooterProps {
  selected: boolean;

  onBack?: () => void;

  onClear?: () => void;

  onNext?: () => void;
}

export default function PreviewFooter({
  selected,
  onBack,
  onClear,
  onNext,
}: PreviewFooterProps) {
  return (
    <div className="flex items-center justify-between border-t border-gray-200 bg-white px-6 py-4">

      {/* Left Buttons */}
      <div className="flex items-center gap-3">

        {/* Back */}
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>

        {/* Clear */}
        <button
          type="button"
          onClick={onClear}
          disabled={!selected}
          className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition
            ${
              selected
                ? "text-red-600 hover:bg-red-50"
                : "cursor-not-allowed text-gray-400"
            }`}
        >
          <RotateCcw className="h-4 w-4" />
          Clear Selection
        </button>

      </div>

      {/* Right Button */}
      <button
        type="button"
        onClick={onNext}
        disabled={!selected}
        className={`inline-flex items-center gap-2 rounded-lg px-6 py-2 text-sm font-semibold transition
          ${
            selected
              ? "bg-indigo-600 text-white hover:bg-indigo-700"
              : "cursor-not-allowed bg-gray-300 text-gray-500"
          }`}
      >
        Analyze Selected Session
        <ArrowRight className="h-4 w-4" />
      </button>

    </div>
  );
}