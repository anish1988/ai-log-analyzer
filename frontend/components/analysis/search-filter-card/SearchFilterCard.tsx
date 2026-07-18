"use client";

import { useState } from "react";
import { ArrowRight, ChevronDown, Filter, RotateCcw } from "lucide-react";
import TextField from "@/components/form/TextField";
import DateField from "@/components/form/DateField";
import ChipSelector from "@/components/form/ChipSelector";
import MultiSelect from "@/components/form/MultiSelect";
import SectionTitle from "@/components/form/SectionTitle";
import { tierOptions } from "@/config/tier-options";
import { serverOptions } from "@/config/server-options";




export interface SearchFiltersState {
  from: string;
  to: string;
  tier: string;
  servers: string[];
  leadId: string;
  campaignId: string;
  uniqueId: string;
  callerId: string;
  callerNumber: string;
  agent: string;
  inboundGroup: string;
}

const initialState: SearchFiltersState = {
  from: "",
  to: "",
  tier: "all",
  servers: ["tel-01", "tel-02"],
  leadId: "",
  campaignId: "",
  uniqueId: "",
  callerId: "",
  callerNumber: "",
  agent: "",
  inboundGroup: "",
};

export interface SearchFilterCardProps {
  onNext?: (filters: SearchFiltersState) => void;
}

export default function SearchFilterCard({ onNext }: SearchFilterCardProps) {
  const [filters, setFilters] = useState<SearchFiltersState>(initialState);

  function update<K extends keyof SearchFiltersState>(
    key: K,
    value: SearchFiltersState[K]
  ) {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8">
      <SectionTitle icon={<Filter className="h-4 w-4" strokeWidth={2} />}>
        Search filters
      </SectionTitle>

      <div className="grid grid-cols-1 gap-x-6 gap-y-5 sm:grid-cols-2">
        <DateField
          label="From"
          required
          value={filters.from}
          onChange={(e) => update("from", e.target.value)}
        />
        <DateField
          label="To"
          required
          value={filters.to}
          onChange={(e) => update("to", e.target.value)}
        />
      </div>

      <div className="mt-5">
        <ChipSelector
          label="Tier"
          options={tierOptions}
          value={filters.tier}
          onChange={(v) => update("tier", v)}
        />
      </div>

      <div className="mt-5">
        <MultiSelect
          label="Server / cluster / IP (multi-select)"
          placeholder="Select servers..."
          options={serverOptions}
          value={filters.servers}
          onChange={(v) => update("servers", v)}
        />
      </div>

      <div className="mt-5 grid grid-cols-1 gap-x-6 gap-y-5 sm:grid-cols-3">
        <TextField
          label="lead_id"
          placeholder="e.g. 48291"
          value={filters.leadId}
          onChange={(e) => update("leadId", e.target.value)}
        />
        <TextField
          label="campaign_id"
          placeholder="e.g. OUTBOUND1"
          value={filters.campaignId}
          onChange={(e) => update("campaignId", e.target.value)}
        />
        <TextField
          label="uniqueid"
          placeholder="e.g. 1718780422.334"
          value={filters.uniqueId}
          onChange={(e) => update("uniqueId", e.target.value)}
        />
        <TextField
          label="callerid"
          placeholder="e.g. <8005551234>"
          value={filters.callerId}
          onChange={(e) => update("callerId", e.target.value)}
        />
        <TextField
          label="caller_number / CID"
          placeholder="e.g. 8005551234"
          value={filters.callerNumber}
          onChange={(e) => update("callerNumber", e.target.value)}
        />
        <TextField
          label="agent / user"
          placeholder="e.g. agent100"
          value={filters.agent}
          onChange={(e) => update("agent", e.target.value)}
        />
      </div>

      <div className="mt-5">
        <TextField
          label="inbound group"
          placeholder="e.g. SALESQ"
          value={filters.inboundGroup}
          onChange={(e) => update("inboundGroup", e.target.value)}
        />
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-lg border border-indigo-200 bg-white px-4 py-2.5 text-sm font-medium text-indigo-600 hover:bg-indigo-50"
        >
          + Add filter...
          <ChevronDown className="h-4 w-4" strokeWidth={2} />
        </button>
        <button
          type="button"
          className="rounded-lg bg-indigo-50 px-4 py-2.5 text-sm font-medium text-indigo-600 hover:bg-indigo-100"
        >
          Add
        </button>
      </div>

      <div className="mt-8 flex flex-col-reverse items-stretch justify-end gap-3 border-t border-slate-100 pt-6 sm:flex-row sm:items-center">
        <button
          type="button"
          onClick={() => setFilters(initialState)}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50"
        >
          <RotateCcw className="h-4 w-4" strokeWidth={2} />
          Clear All
        </button>
        <button
          type="button"
          onClick={() => onNext?.(filters)}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-500"
        >
          Next
          <ArrowRight className="h-4 w-4" strokeWidth={2} />
        </button>
      </div>
    </div>
  );
}