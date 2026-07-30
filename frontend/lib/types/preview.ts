/**
 * Types for Step 2 – Preview Sessions
 *
 * The backend endpoint (POST /api/logs/fetch) returns matched log lines
 * grouped by file. On the frontend we render each grouped file result as
 * a "session card" that the user can select before moving on to Step 3
 * (AI analysis).
 *
 * Keep the *Raw types (LogLine, FileResult, LogFetchResponse) in perfect
 * sync with the backend Pydantic schemas. Anything UI-specific (counts,
 * derived timestamps, selection state) lives on MatchedSession.
 */

// ---------------------------------------------------------------------------
// Raw backend response
// ---------------------------------------------------------------------------

/** A single matched log line as returned by the backend. */
export interface LogLine {
  server: string;
  file: string;
  file_id: string;
  line_number: number;
  raw: string;
  /** Which filter keys (e.g. "lead_id", "outbound") matched this line. */
  matched_filters: string[];
}

/** Metadata echoed back by the backend for a file result. */
export interface FileResultMeta {
  leadid?: string;
  outbound?: string;
  // Allow forward-compatible extra keys without breaking the type.
  [key: string]: string | undefined;
}

/** One grouped file result — becomes one card in the UI. */
export interface FileResult {
  file_id: string;
  file_label: string;
  server: string;
  searched_file: string;
  meta: FileResultMeta;
  matched_count: number;
  lines: LogLine[];
}

/** Top-level response from POST /api/logs/fetch. */
export interface LogFetchResponse {
  total_lines: number;
  results: FileResult[];
}

// ---------------------------------------------------------------------------
// Step-1 filters payload (sent when triggering the fetch)
// ---------------------------------------------------------------------------

export interface SearchFilters {
  lead_id?: string;
  outbound?: string;
  unique_id?: string;
  phone?: string;
  date?: string;          // ISO yyyy-MM-dd
  time_from?: string;     // HH:mm
  time_to?: string;       // HH:mm
  servers?: string[];
  file_ids?: string[];    // which log files to search
  keywords?: string[];
}

// ---------------------------------------------------------------------------
// UI view-model (derived — not sent by backend)
// ---------------------------------------------------------------------------

export type SessionSeverity = "error" | "warning" | "info";

/**
 * A MatchedSession is what a SessionCard renders. It is built from a
 * FileResult via `toMatchedSession()` in lib/utils/previewHelpers.ts.
 */
export interface MatchedSession {
  /** Stable id used for selection — we use file_id from backend. */
  id: string;
  /** Human title shown on the card, e.g. "FASTagiout". */
  title: string;
  /** Short subtitle, e.g. "astguiclient/FASTagiout.2026-07-21". */
  subtitle: string;

  leadId?: string;
  campaign?: string;
  servers: string[];

  /** First & last timestamp parsed from matched lines (may be undefined). */
  startTime?: string;
  endTime?: string;

  lineCount: number;
  errorCount: number;
  warningCount: number;

  /** Short human summary — optional, filled in later by AI/heuristics. */
  summary?: string;

  /** Keep the original file result around for Step 3. */
  raw: FileResult;
}

/** Convenience: the shape a stat badge needs. */
export interface SessionStat {
  label: string;
  value: number;
  severity: SessionSeverity;
}
