// frontend/app/new-analysis/page.tsx
"use client";

import { useState } from "react";
import { SearchFiltersProvider, SearchFiltersState } from "@/providers/SearchFiltersProvider";
import SearchFilterCard from "@/components/analysis/search-filter-card/SearchFilterCard";
import type {
  LogFetchResponse,
  WebLogFetchResponse,
} from "@/lib/types/preview";

import ResultRenderer from "@/components/analysis/result-renderer/ResultRenderer";
import Stepper from "@/components/stepper/Stepper";
import { buildRequestSignature } from "@/lib/utils/requestSignature";
import { AnalysisCache } from "@/lib/types/analysisCache";
// import PreviewSession from "@/components/analysis/preview-session/PreviewSession";

export default function NewAnalysisPage() {
  const [step, setStep] = useState(1);
  const goToStep1 = () => {
  setStep(1);
};

const goToStep2 = () => {
  setStep(2);
};
  const [analysisResult, setAnalysisResult] = useState<LogFetchResponse | WebLogFetchResponse | null>(null);
const [requestSignature, setRequestSignature] =
  useState("");

const [cachedFilters, setCachedFilters] =
  useState<SearchFiltersState | null>(null);
  const [analysisCache, setAnalysisCache] =
    useState<AnalysisCache | null>(null);

  return (
    <SearchFiltersProvider>
      <div className="mx-auto max-w-7xl px-6 py-8">
        <Stepper currentStep={step} />
        <div className="mt-8">
        {step === 1 && (
          
          // <SearchFilterCard  onNext={(response) => {  setAnalysisResult(response);  setStep(2);  }} />
          <SearchFilterCard
        onNext={(response) => {

        console.log("=================================");
        console.log("STEP-2");
        console.log("Tier :", response);
        console.log("=================================");

        setAnalysisResult(response);

        goToStep2();

    }}
/>
      
      
      
      )}

       {step === 2 && analysisResult && (
          <ResultRenderer
              tier={analysisResult.success ? "web" : "telephony"}
              data={analysisResult}
              onBack={goToStep1}
          />
    )}
    </div>
      </div>
    </SearchFiltersProvider>
  );
}