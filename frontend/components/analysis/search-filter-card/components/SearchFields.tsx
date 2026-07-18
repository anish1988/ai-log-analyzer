"use client";

import TextField from "@/components/form/TextField";
import { useSearchFilters } from "@/hooks/useSearchFilters";

export default function SearchFields() {
  const { filters, setField } = useSearchFilters();

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 gap-x-6 gap-y-5 sm:grid-cols-3">
        <TextField
          label="lead_id"
          placeholder="e.g. 48291"
          value={filters.leadId}
          onChange={(e) => setField("leadId", e.target.value)}
        />
        <TextField
          label="campaign_id"
          placeholder="e.g. OUTBOUND1"
          value={filters.campaignId}
          onChange={(e) => setField("campaignId", e.target.value)}
        />
        <TextField
          label="uniqueid"
          placeholder="e.g. 1718780422.334"
          value={filters.uniqueId}
          onChange={(e) => setField("uniqueId", e.target.value)}
        />
        <TextField
          label="callerid"
          placeholder="e.g. <8005551234>"
          value={filters.callerId}
          onChange={(e) => setField("callerId", e.target.value)}
        />
        <TextField
          label="caller_number / CID"
          placeholder="e.g. 8005551234"
          value={filters.callerNumber}
          onChange={(e) => setField("callerNumber", e.target.value)}
        />
        <TextField
          label="agent / user"
          placeholder="e.g. agent100"
          value={filters.agent}
          onChange={(e) => setField("agent", e.target.value)}
        />
      </div>

      <TextField
        label="inbound group"
        placeholder="e.g. SALESQ"
        value={filters.inboundGroup}
        onChange={(e) => setField("inboundGroup", e.target.value)}
      />
    </div>
  );
}