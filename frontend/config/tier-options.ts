import type { TierSelection } from "@/types/log-analysis";

export interface TierOption {
  label: string;
  value: TierSelection;
}

export const tierOptions: TierOption[] = [
  { label: "All", value: "all" },
  { label: "Web", value: "web" },
  { label: "DB", value: "db" },
  { label: "Telephony", value: "telephony" },
];