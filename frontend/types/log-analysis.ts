export type Tier = "web" | "db" | "telephony";

export type TierSelection = "all" | Tier;

export interface SearchFiltersState {
  from: string;
  to: string;

  tier: TierSelection;

  servers: string[];

  leadId: string;
  campaignId: string;
  uniqueId: string;
  callerId: string;
  callerNumber: string;
  agent: string;
  inboundGroup: string;

  logType: string;

  defaultLogPath: string;
  customLogPath: string;
}
