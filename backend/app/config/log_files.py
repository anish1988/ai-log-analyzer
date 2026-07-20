"""
Which log files get searched for a given tier. Selecting "Web" only ever
searches the web-tagged entries below; "Telephony" only searches the
telephony ones, and so on. Adding a new log file for a tier is just a new
entry here - no resolver/fetch code changes.
"""
from dataclasses import dataclass

from app.config.servers import Tier

import os

LOG_ROOT = os.getenv("LOCAL_LOG_ROOT", "/var/log")


@dataclass(frozen=True)
class LogFileConfig:
    id: str
    tier: Tier
    label: str
    service: str  # apache | mysql | asterisk-core | asterisk-full | vicidial | ...
    remote_path_template: str  # use {date} as the placeholder
    has_date_pattern: bool
    gzip_after_days: int = 3
    date_pattern: str = "%d-%m-%Y"  # matches messages_18-07-2026


LOG_FILE_REGISTRY: list[LogFileConfig] = [
    # --- Web tier (point 3: no date suffix - static path, searched as-is) ---
    LogFileConfig(
        id="web-apache-access", tier=Tier.WEB, label="Apache Access", service="apache",
        remote_path_template=f"{LOG_ROOT}/apache2/access.log", has_date_pattern=False,
    ),
    LogFileConfig(
        id="web-apache-error", tier=Tier.WEB, label="Apache Error", service="apache",
        remote_path_template=f"{LOG_ROOT}/apache2/error.log", has_date_pattern=False,
    ),
    LogFileConfig(
        id="web-apache-error", tier=Tier.WEB, label="Apache Error", service="apache",
        remote_path_template=f"{LOG_ROOT}/syslog.log", has_date_pattern=False,
    ),
    LogFileConfig(
        id="web-mysql", tier=Tier.WEB, label="MySQL", service="mysql",
        remote_path_template=f"{LOG_ROOT}/mysql/error.log", has_date_pattern=False,
    ),

    # --- Telephony tier (multiple log files per server, e.g. tel-01 has several) ---
    LogFileConfig(
        id="tel-messages", tier=Tier.TELEPHONY, label="Messages", service="asterisk-core",
        remote_path_template=f"{LOG_ROOT}/asterisk/messages_{{date}}", has_date_pattern=True,
    ),
    LogFileConfig(
        id="tel-full", tier=Tier.TELEPHONY, label="Full", service="asterisk-full",
        remote_path_template=f"{LOG_ROOT}/asterisk/full_{{date}}", has_date_pattern=True,
    ),
    LogFileConfig(
        id="tel-vicidial-log", tier=Tier.TELEPHONY, label="VICIdial Log", service="vicidial",
        # Doesn't rotate by date - searched directly.
        remote_path_template=f"{LOG_ROOT}/astguiclient/vicidial.log", has_date_pattern=False,
    ),

    # --- DB tier (point 3: no date suffix - static path, searched as-is) ---
    LogFileConfig(
        id="db-slow-query", tier=Tier.DB, label="Slow Query", service="mysql",
        remote_path_template=f"{LOG_ROOT}/mysql/slow-query.log", has_date_pattern=False,
    ),
]


def get_log_files_for_tier(tier: Tier) -> list[LogFileConfig]:
    return [f for f in LOG_FILE_REGISTRY if f.tier == tier]