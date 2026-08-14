// frontend/app/new-analysis/page.tsx
"use client";

import { useState } from "react";

import {
  SearchFiltersProvider,
} from "@/providers/SearchFiltersProvider";

import SearchFilterCard from "@/components/analysis/search-filter-card/SearchFilterCard";

import type {
  LogFetchResponse,
  WebLogFetchResponse,
} from "@/lib/types/preview";

import type {
  AIAnalysisResponse,
} from "@/lib/types/aiAnalysis";

import ResultRenderer from "@/components/analysis/result-renderer/ResultRenderer";

import AIAnalysisResultContainer from "@/components/analysis/ai-analysis/AIAnalysisResultContainer";

import Stepper from "@/components/stepper/Stepper";

// =============================================================================
// PAGE
// =============================================================================

export default function NewAnalysisPage() {

  // ===========================================================================
  // STEP
  // ===========================================================================

  const [step, setStep] = useState(1);

  // ===========================================================================
  // LOG ANALYSIS RESULT
  // ===========================================================================

  const [
    analysisResult,
    setAnalysisResult,
  ] = useState<
    LogFetchResponse |
    WebLogFetchResponse |
    null
  >(null);

  // ===========================================================================
  // AI ANALYSIS RESPONSE
  // ===========================================================================

  const [
    aiAnalysisResponse,
    setAIAnalysisResponse,
  ] = useState<
    AIAnalysisResponse | null
  >(null);

  // ===========================================================================
  // STEP NAVIGATION
  // ===========================================================================

  const goToStep1 = () => {
    setStep(1);
  };

  const goToStep2 = () => {
    setStep(2);
  };

  const goToStep3 = () => {
    setStep(3);
  };

  // ===========================================================================
  // STEP 1 → STEP 2
  // ===========================================================================

  const handleLogAnalysisCompleted = (
    response:
      | LogFetchResponse
      | WebLogFetchResponse,
  ) => {

    console.log(
      "=================================",
    );

    console.log(
      "LOG ANALYSIS COMPLETED",
    );

    console.log(
      response,
    );

    console.log(
      "=================================",
    );

    setAnalysisResult(
      response,
    );

    goToStep2();
  };

  // ===========================================================================
  // STEP 2 → STEP 3
  // ===========================================================================
  //
  // This callback is triggered by WebResult after the AI analysis popup
  // has completed and the user closes the popup.
  //
  // IMPORTANT:
  // We do NOT start another LLM request here.
  //
  // The response is the already completed AI analysis response.
  // ===========================================================================

  const handleAIAnalysisCompleted = (
    response: AIAnalysisResponse,
  ) => {

    console.log(
      "=================================",
    );

    console.log(
      "AI ANALYSIS COMPLETED",
    );

    console.log(
      response,
    );

    console.log(
      "Moving to STEP 3",
    );

    console.log(
      "=================================",
    );

    // Store the already completed AI response.
    setAIAnalysisResponse(
      response,
    );

    // Replace Step 2 with Step 3.
    goToStep3();
  };

  // ===========================================================================
  // STEP 3 → STEP 2
  // ===========================================================================

 

  // ===========================================================================
  // RENDER
  // ===========================================================================

  return (
    <SearchFiltersProvider>

      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* ================================================================== */}
        {/* STEPPER                                                            */}
        {/* ================================================================== */}

        <Stepper
          currentStep={step}
        />

        <div className="mt-8">

          {/* ================================================================ */}
          {/* STEP 1                                                           */}
          {/* ================================================================ */}

          {step === 1 && (
            <SearchFilterCard
              onNext={
                handleLogAnalysisCompleted
              }
            />
          )}

          {/* ================================================================ */}
          {/* STEP 2                                                           */}
          {/* ================================================================ */}

          {step === 2 &&
            analysisResult && (
              <ResultRenderer
                tier={
                  analysisResult.success
                    ? "web"
                    : "telephony"
                }
                data={
                  analysisResult
                }
                onBack={
                  goToStep1
                }
                onAIAnalysisCompleted={
                  handleAIAnalysisCompleted
                }
              />
            )}

          {/* ================================================================ */}
          {/* STEP 3                                                           */}
          {/* ================================================================ */}

          {step === 3 &&
            aiAnalysisResponse && (
              <AIAnalysisResultContainer
                response={
                  aiAnalysisResponse
                }
              />
            )}

        </div>

      </div>

    </SearchFiltersProvider>
  );
}