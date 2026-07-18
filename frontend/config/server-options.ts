import type { ServerConfig } from "@/components/analysis/search-filter-card/types";

/**
 * Single source of truth for every server the analyzer can reach.
 * The UI only ever knows a server by its `id` (e.g. "tel-01"); everything
 * that needs the real IP/SSH user resolves it here.
 *
 * TODO: once this stabilizes, move to env vars or a DB table instead of a
 * checked-in file, especially for anything touching credentials.
 */
export const SERVER_REGISTRY: ServerConfig[] = [
  { id: "web-01", label: "web-01", tier: "web", ip: "10.10.1.11", sshPort: 22, sshUser: "deploy" },
  { id: "web-02", label: "web-02", tier: "web", ip: "10.10.1.12", sshPort: 22, sshUser: "deploy" },

  { id: "db-01", label: "db-01", tier: "db", ip: "10.10.2.11", sshPort: 22, sshUser: "deploy" },

  { id: "tel-01", label: "tel-01", tier: "telephony", ip: "10.10.3.11", sshPort: 22, sshUser: "deploy" },
  { id: "tel-02", label: "tel-02", tier: "telephony", ip: "10.10.3.12", sshPort: 22, sshUser: "deploy" },
  { id: "tel-03", label: "tel-03", tier: "telephony", ip: "10.10.3.13", sshPort: 22, sshUser: "deploy" },
];