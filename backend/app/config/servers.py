"""
Single source of truth for every server the analyzer can reach.
The frontend only ever sends a server `id` (e.g. "tel-01") - everything that
needs the real IP / SSH user resolves it here. Never expose this list (or
its contents) back to the frontend.

TODO: move to env vars / a DB table once this stabilizes, especially the
SSH credentials.
"""
from dataclasses import dataclass
from enum import Enum


class Tier(str, Enum):
    WEB = "web"
    DB = "db"
    TELEPHONY = "telephony"


@dataclass(frozen=True)
class ServerConfig:
    id: str
    label: str
    tier: Tier
    ip: str
    ssh_port: int
    ssh_user: str


SERVER_REGISTRY: list[ServerConfig] = [
    ServerConfig(id="web-01", label="web-01", tier=Tier.WEB, ip="127.0.0.1", ssh_port=22, ssh_user="deploy"),
    ServerConfig(id="web-02", label="web-02", tier=Tier.WEB, ip="127.0.0.1", ssh_port=22, ssh_user="deploy"),

    ServerConfig(id="db-01", label="db-01", tier=Tier.DB, ip="10.10.2.11", ssh_port=22, ssh_user="deploy"),

    ServerConfig(id="tel-01", label="tel-01", tier=Tier.TELEPHONY, ip="10.10.3.11", ssh_port=22, ssh_user="deploy"),
    ServerConfig(id="tel-02", label="tel-02", tier=Tier.TELEPHONY, ip="10.10.3.12", ssh_port=22, ssh_user="deploy"),
    ServerConfig(id="tel-03", label="tel-03", tier=Tier.TELEPHONY, ip="10.10.3.13", ssh_port=22, ssh_user="deploy"),

   # --- Local dev/testing only (ip="local" triggers the LOCAL_HOSTS branch
    # in log_analysis_service.py -> reads local-test-logs/... via the
    # docker-compose volume mount instead of SSH). Remove before prod deploy.
    ServerConfig(id="local-web", label="local-web (dev)", tier=Tier.WEB, ip="127.0.0.1", ssh_port=22, ssh_user="dev"),
    ServerConfig(id="local-db", label="local-db (dev)", tier=Tier.DB, ip="127.0.0.1", ssh_port=22, ssh_user="dev"),
    ServerConfig(id="local-tel", label="local-tel (dev)", tier=Tier.TELEPHONY, ip="local", ssh_port=22, ssh_user="dev"),
]
 

def get_server_by_id(server_id: str) -> ServerConfig | None:
    return next((s for s in SERVER_REGISTRY if s.id == server_id), None)


def get_selectable_servers(tier: str) -> list[ServerConfig]:
    """'all' -> every server across tiers; a single tier -> only that tier's servers."""
    if tier == "all":
        return SERVER_REGISTRY
    return [s for s in SERVER_REGISTRY if s.tier.value == tier]