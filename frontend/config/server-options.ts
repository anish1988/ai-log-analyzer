import type { Tier, TierSelection } from "@/types/log-analysis";

export interface ServerOption {
  id: string;
  label: string;
  tier: Tier;
}

/**
 * Frontend-safe server list — id + display label + tier only. Real IPs and
 * SSH credentials live exclusively in backend/app/config/servers.py and are
 * never sent to the browser. Keep these ids in sync with that file.
 */
export const SERVER_REGISTRY: ServerOption[] = [
  { id: "web-01", label: "web-01", tier: "web" },
  { id: "web-02", label: "web-02", tier: "web" },

  { id: "db-01", label: "db-01", tier: "db" },

  { id: "tel-01", label: "tel-01", tier: "telephony" },
  { id: "tel-02", label: "tel-02", tier: "telephony" },
  { id: "tel-03", label: "tel-03", tier: "telephony" },

   // Local dev/testing only - mirrors backend/app/config/servers.py's
  // local-* entries (ip="local", reads local-test-logs/ via the
  // docker-compose volume mount instead of SSH). Remove before prod deploy.
  { id: "local-web", label: "local-web (dev)", tier: "web" },
  { id: "local-db", label: "local-db (dev)", tier: "db" },
  { id: "local-tel", label: "local-tel (dev)", tier: "telephony" },
];

/**
 * Point 3/4: "all" -> every server, across every tier.
 * A single tier -> only that tier's servers, in the {label, value} shape
 * MultiSelect expects.
 */
export function getServerOptionsForTier(tier: TierSelection) {
  const servers = tier === "all" ? SERVER_REGISTRY : SERVER_REGISTRY.filter((s) => s.tier === tier);
  return servers.map(({ id, label }) => ({ label, value: id }));
}