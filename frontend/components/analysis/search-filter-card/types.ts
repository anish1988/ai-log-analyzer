export interface SearchFiltersUI {
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