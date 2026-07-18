import type { LogFileConfig } from "@/lib/log-analysis/types";

/**
 * Which log files get searched for a given tier. Selecting "Web" only ever
 * searches the web-tagged entries below; selecting "Telephony" only searches
 * the telephony ones, and so on. Adding a new log file for a tier is just a
 * new entry here — no resolver/fetch code changes.
 */
export const LOG_FILE_REGISTRY: LogFileConfig[] = [
  // --- Web tier ---
  {
    id: "web-apache-access",
    tier: "web",
    label: "Apache Access",
    service: "apache",
    remotePathTemplate: "/var/log/httpd/access_{date}.log",
    hasDatePattern: true,
    datePattern: "dd-MM-yyyy",
    gzipAfterDays: 3,
  },
  {
    id: "web-apache-error",
    tier: "web",
    label: "Apache Error",
    service: "apache",
    remotePathTemplate: "/var/log/httpd/error_{date}.log",
    hasDatePattern: true,
    datePattern: "dd-MM-yyyy",
    gzipAfterDays: 3,
  },
  {
    id: "web-mysql",
    tier: "web",
    label: "MySQL",
    service: "mysql",
    remotePathTemplate: "/var/log/mysql/mysql_{date}.log",
    hasDatePattern: true,
    datePattern: "dd-MM-yyyy",
    gzipAfterDays: 3,
  },

  // --- Telephony tier (multiple log files per server, e.g. tel-01 has several) ---
  {
    id: "tel-messages",
    tier: "telephony",
    label: "Messages",
    service: "asterisk-core",
    remotePathTemplate: "/var/log/asterisk/messages_{date}",
    hasDatePattern: true,
    datePattern: "dd-MM-yyyy",
    gzipAfterDays: 3,
  },
  {
    id: "tel-full",
    tier: "telephony",
    label: "Full",
    service: "asterisk-full",
    remotePathTemplate: "/var/log/asterisk/full_{date}",
    hasDatePattern: true,
    datePattern: "dd-MM-yyyy",
    gzipAfterDays: 3,
  },
  {
    id: "tel-vicidial-log",
    tier: "telephony",
    label: "VICIdial Log",
    service: "vicidial",
    // Doesn't rotate by date (point 12) — searched directly.
    remotePathTemplate: "/var/log/astguiclient/vicidial.log",
    hasDatePattern: false,
    gzipAfterDays: 3,
  },

  // --- DB tier ---
  {
    id: "db-slow-query",
    tier: "db",
    label: "Slow Query",
    service: "mysql",
    remotePathTemplate: "/var/log/mysql/slow-query_{date}.log",
    hasDatePattern: true,
    datePattern: "dd-MM-yyyy",
    gzipAfterDays: 3,
  },
];