// frontend/app/new-analysis/page.tsx
"use client";

import { useState } from "react";
import { SearchFiltersProvider } from "@/providers/SearchFiltersProvider";
import SearchFilterCard from "@/components/analysis/search-filter-card/SearchFilterCard";
import type {
  LogFetchResponse,
  WebLogFetchResponse,
} from "@/lib/types/preview";

import ResultRenderer from "@/components/analysis/result-renderer/ResultRenderer";
// import PreviewSession from "@/components/analysis/preview-session/PreviewSession";

export default function NewAnalysisPage() {
  const [step, setStep] = useState(1);
  const [analysisResult, setAnalysisResult] = useState<LogFetchResponse | WebLogFetchResponse | null>(null);
  return (
    <SearchFiltersProvider>
      <div className="mx-auto max-w-4xl px-6 py-8">
        {step === 1 && (
          
          // <SearchFilterCard  onNext={(response) => {  setAnalysisResult(response);  setStep(2);  }} />
          <SearchFilterCard
    onNext={(response) => {

        console.log("=================================");
        console.log("STEP-2");
        console.log("Tier :", response);
        console.log("=================================");

        setAnalysisResult(response);

        setStep(2);

    }}
/>
      
      
      
      )}

       {step === 2 && analysisResult && (
          <ResultRenderer
              tier={analysisResult.success ? "web" : "telephony"}
              data={analysisResult}
          />
    )}
      </div>
    </SearchFiltersProvider>
  );
}