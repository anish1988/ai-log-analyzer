import { Funnel } from "lucide-react";

import SectionTitle from "@/components/form/SectionTitle";

import DateRangeSection from "./components/DateRangeSection";
import TierSection from "@/components/search/TierSection";
import ServerSelection from "./components/ServerSelection";
import SearchFields from "./components/SearchFields";
import ActionButtons from "./components/ActionButtons";

export default function SearchFilterCard() {
  return (
    <section
      className="
        mt-6
        rounded-2xl
        border
        border-slate-200
        bg-white
        shadow-sm
      "
    >
      <div className="p-8">

        <SectionTitle
          title="Search filters"
          icon={<Funnel className="h-5 w-5 text-indigo-600" />}
        />

        <div className="space-y-8">

          <DateRangeSection />

          <TierSection />

          <ServerSelection />

          <SearchFields />

        </div>

      </div>

      <div
        className="
          border-t
          border-slate-200
          px-8
          py-6
        "
      >
        <ActionButtons />
      </div>
    </section>
  );
}