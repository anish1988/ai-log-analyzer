"""
Registry of searchable log files.

This file is intentionally environment-independent.

It DOES NOT contain filesystem paths.

The actual filesystem paths are resolved by:

    search_local_file()
    search_remote_file()

This allows:

LOCAL
------
/host_logs/apache2/error.log

REMOTE
-------
/var/log/httpd/error_log
/var/log/apache2/error.log

without changing this registry.
"""

from dataclasses import dataclass

from app.config.servers import Tier


@dataclass(frozen=True)
class LogFileConfig:
    id: str

    tier: Tier

    label: str

    #
    # apache
    # mysql
    # syslog
    # messages
    # asterisk-core
    # asterisk-full
    # vicidial
    #
    service: str

    #
    # Relative filename only.
    #
    # Examples
    #
    # access.log
    # error.log
    # messages_{date}
    #
    filename: str

    #
    # Whether filename contains {date}
    #
    has_date_pattern: bool

    filename_template: str | None = None

    #
    # After N days resolver will first try .gz
    #
    gzip_after_days: int = 3

    date_pattern: str = "%Y-%m-%d"


LOG_FILE_REGISTRY = [

    #
    # WEB
    #



    LogFileConfig(
        id="web-apache-error",
        tier=Tier.WEB,
        label="Apache Error",
        service="apache",
        filename="error.log",
        filename_template="error.log",
        has_date_pattern=False,
    ),
    LogFileConfig(
        id="web-apache-error",
        tier=Tier.WEB,
        label="Apache Error",
        service="apache",
        filename="access.log",
        filename_template="access.log",
        has_date_pattern=False,
    ),
]


def get_log_files_for_tier(tier: Tier) -> list[LogFileConfig]:

    return [
        file
        for file in LOG_FILE_REGISTRY
        if file.tier == tier
    ]