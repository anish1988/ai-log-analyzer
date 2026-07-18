/**
 * Shared types for the search-filters -> tier/server resolution -> SSH fetch
 * pipeline. Kept framework-agnostic so they can be reused by the React hooks,
 * the Next.js API routes, and (if you port the fetch step to Python) as the
 * contract your LangGraph/asyncssh service should mirror.
 */

export type Tier = "web" | "db" | "telephony";
export type TierSelection = Tier | "all";

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
}

export interface ServerConfig {
  id: string; // e.g. "web-01" — the id used in SearchFiltersState.servers
  label: string;
  tier: Tier;
  ip: string;
  sshPort: number;
  sshUser: string;
}

export interface LogFileConfig {
  id: string;
  tier: Tier;
  label: string;
  /** apache | mysql | asterisk-core | asterisk-full | vicidial | ... */
  service: string;
  /** Use `{date}` as the placeholder, e.g. "/var/log/asterisk/messages_{date}" */
  remotePathTemplate: string;
  /** Not every log file rotates daily — set false to search the static path directly. */
  hasDatePattern: boolean;
  datePattern?: "dd-MM-yyyy";
  /** Files older than this many days are expected to be gzip-compressed on disk. */
  gzipAfterDays: number;
}

export interface SearchTerm {
  key: keyof SearchFiltersState;
  value: string;
}

export interface LogLine {
  server: string;
  file: string;
  fileId: string;
  lineNumber: number;
  raw: string;
  /** Which filter fields matched this specific line (a line can match more than one). */
  matchedFilters: string[];
}

export interface LogFileResult {
  fileId: string;
  fileLabel: string;
  server: string;
  meta: Record<string, string>;
  lines: LogLine[];
}

export interface LogFetchResponse {
  totalLines: number;
  results: LogFileResult[];
}

export interface PermissionCheckRequest {
  tier: TierSelection;
  servers: string[];
}

export interface PermissionCheckResponse {
  granted: boolean;
  message?: string;
}