"use client";

import type { ReactNode } from "react";

import type {
  AIAnalysisResult,
} from "@/lib/types/aiAnalysis";

import AIAnalysisState from "./AIAnalysisState";

interface AIAnalysisResultStateProps {
  result: AIAnalysisResult | null;

  loading?: boolean;

  error?: string | null;

  onRetry?: () => void;

  onBack?: () => void;

  children: ReactNode;
}

export default function AIAnalysisResultState({
  result,
  loading = false,
  error = null,
  onRetry,
  onBack,
  children,
}: AIAnalysisResultStateProps) {
  if (loading) {
    return (
      <AIAnalysisState
        type="loading"
        onBack={onBack}
      />
    );
  }

  if (error) {
    return (
      <AIAnalysisState
        type="error"
        message={error}
        onRetry={onRetry}
        onBack={onBack}
      />
    );
  }

  if (!result) {
    return (
      <AIAnalysisState
        type="empty"
        onBack={onBack}
      />
    );
  }

  return <>{children}</>;
}