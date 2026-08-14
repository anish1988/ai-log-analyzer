"use client";

import type { AIProgressEvent } from "@/hooks/useAIAnalysisProgress";

import AIAnalysisProgressHeader from "./AIAnalysisProgressHeader";
import AIAnalysisProgressBar from "./AIAnalysisProgressBar";
import AIAnalysisTaskTimeline from "./AIAnalysisTaskTimeline";
import AIAnalysisProgressDetails from "./AIAnalysisProgressDetails";

interface AIAnalysisProgressProps {
  progress: AIProgressEvent | null;

  isAnalyzing: boolean;

  isCompleted?: boolean;

  error?: string | null;
}

export default function AIAnalysisProgress({
  progress,
  isAnalyzing,
  isCompleted = false,
  error = null,
}: AIAnalysisProgressProps) {
  if (!isAnalyzing && !isCompleted && !error) {
    return null;
  }

  return (
    <section
      aria-live="polite"
      aria-busy={isAnalyzing}
      className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
    >
      {/* ------------------------------------------------------------------ */}
      {/* Header                                                             */}
      {/* ------------------------------------------------------------------ */}

      <AIAnalysisProgressHeader
        progress={progress}
        isAnalyzing={isAnalyzing}
        isCompleted={isCompleted}
        error={error}
      />

      {/* ------------------------------------------------------------------ */}
      {/* Main Progress Area                                                 */}
      {/* ------------------------------------------------------------------ */}

      <div className="space-y-6 px-6 py-6">
        {/* Progress Bar */}

        <AIAnalysisProgressBar
          progress={progress}
        />

        {/* Task Timeline */}

        <AIAnalysisTaskTimeline
          progress={progress}
        />

        {/* Technical / Current Error Details */}

        <AIAnalysisProgressDetails
          progress={progress}
        />
      </div>
    </section>
  );
}