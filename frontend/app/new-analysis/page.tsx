// frontend/app/new-analysis/page.tsx
"use client";

import { useState } from "react";
import { SearchFiltersProvider } from "@/providers/SearchFiltersProvider";
import SearchFilterCard from "@/components/analysis/search-filter-card/SearchFilterCard";

export default function NewAnalysisPage() {
  const [step, setStep] = useState(1);
    
  return (
    <SearchFiltersProvider>
      <div className="mx-auto max-w-4xl px-6 py-8">
        {step === 1 && <SearchFilterCard onNext={() => setStep(2)} />}
        {step === 2 && <div>Step 2 — Additional Info (placeholder)</div>}
      </div>
    </SearchFiltersProvider>
  );
}