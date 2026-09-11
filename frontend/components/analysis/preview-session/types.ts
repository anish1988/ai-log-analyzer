import type { LogLine } from "@/lib/types/preview";

export interface SessionField {
  label: string;
  value: string;
}

export interface SessionStat {
  label: string;
  value: number;
}

export interface Session {
  id: string;
  title: string;
  server: string;
  searchedFile: string;
  matchedCount: number;
  fields: SessionField[];
  stats: SessionStat[];
  lines: LogLine[];
  raw: unknown;
}
