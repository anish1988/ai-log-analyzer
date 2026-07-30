// frontend/app/new-analysis/page.tsx
"use client";

import { useState } from "react";
import { SearchFiltersProvider } from "@/providers/SearchFiltersProvider";
import SearchFilterCard from "@/components/analysis/search-filter-card/SearchFilterCard";
import type { LogFetchResponse } from "@/lib/log-analysis/types";
import PreviewSession from "@/components/analysis/preview-session/PreviewSession";

export default function NewAnalysisPage() {
  const [step, setStep] = useState(1);
  const [analysisResult, setAnalysisResult] = useState<LogFetchResponse | null>(null); 
  return (
    <SearchFiltersProvider>
      <div className="mx-auto max-w-4xl px-6 py-8">
        {step === 1 && (<SearchFilterCard  onNext={(response) => {  setAnalysisResult(response);  setStep(2);  }} />)}

        {step === 2 && analysisResult && (
        <PreviewSession data={analysisResult} />
        )}
      </div>
    </SearchFiltersProvider>
  );
}